#!/usr/bin/env python3
"""
Builds one calendar feed containing:
  1. Every upcoming event at O2 Victoria Warehouse Manchester (via the Ticketmaster Discovery API)
  2. Manchester United men's HOME games (filtered from the club's official calendar feed)

Environment variables:
  TM_API_KEY    Free Ticketmaster Discovery API key (developer.ticketmaster.com)
  MUFC_ICS_URL  The Man Utd men's fixtures calendar link (from manutd.com/en/team-fixture-calendars)
  TM_VENUE_ID   Optional. Skip the venue lookup if you already know the Ticketmaster venue id
  OUTPUT_PATH   Optional. Defaults to docs/old-trafford.ics

If either source fails, the script exits with an error and does NOT overwrite the existing
calendar, so a temporary outage never wipes your events.
"""
import datetime as dt
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from icalendar import Calendar, Event

LONDON = ZoneInfo("Europe/London")
TM_BASE = "https://app.ticketmaster.com/discovery/v2"
OUTPUT = Path(os.environ.get("OUTPUT_PATH", "docs/old-trafford.ics"))

VW_ADDRESS = "O2 Victoria Warehouse, Trafford Wharf Road, Manchester M17 1AB"
VW_DEFAULT_LENGTH = dt.timedelta(hours=4)
# Ticketmaster often lists add-ons as separate "events"; skip them so each night appears once
SKIP_WORDS = ("vip", "upgrade", "parking", "package", "hospitality", "cloakroom")

UNITED_NAMES = ("manchester united", "man utd", "man united", "man. united")


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Missing environment variable {name}")
    return value


def get_json(url, params):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------- Victoria Warehouse

def find_venue_id(api_key):
    if os.environ.get("TM_VENUE_ID"):
        return os.environ["TM_VENUE_ID"].strip()
    data = get_json(f"{TM_BASE}/venues.json",
                    {"apikey": api_key, "keyword": "Victoria Warehouse", "countryCode": "GB"})
    for venue in data.get("_embedded", {}).get("venues", []):
        if "manchester" in venue.get("city", {}).get("name", "").lower():
            print(f"Ticketmaster venue: {venue['name']} (id {venue['id']}) "
                  f"- save this as TM_VENUE_ID to skip the lookup")
            return venue["id"]
    sys.exit("Couldn't find O2 Victoria Warehouse on Ticketmaster")


def victoria_warehouse_events(api_key):
    venue_id = find_venue_id(api_key)
    raw, page = [], 0
    while True:
        data = get_json(f"{TM_BASE}/events.json",
                        {"apikey": api_key, "venueId": venue_id, "size": 100,
                         "page": page, "sort": "date,asc"})
        raw += data.get("_embedded", {}).get("events", [])
        page += 1
        total_pages = data.get("page", {}).get("totalPages", 0)
        if page >= total_pages or page * 100 >= 1000:  # API caps deep paging at 1000 results
            break

    events, seen = [], set()
    for e in raw:
        name = e.get("name", "").strip()
        start = e.get("dates", {}).get("start", {})
        day = start.get("localDate")
        if not name or not day or any(w in name.lower() for w in SKIP_WORDS):
            continue
        if (name.lower(), day) in seen:
            continue
        seen.add((name.lower(), day))

        ev = Event()
        ev.add("uid", f"tm-{e['id']}@old-trafford-calendar")
        ev.add("dtstamp", dt.datetime.now(dt.timezone.utc))
        ev.add("summary", f"Victoria Warehouse: {name}")
        ev.add("location", VW_ADDRESS)
        if e.get("url"):
            ev.add("url", e["url"])
            ev.add("description", f"Tickets and info: {e['url']}")

        date = dt.date.fromisoformat(day)
        if start.get("localTime"):
            t = dt.time.fromisoformat(start["localTime"])
            begin = dt.datetime.combine(date, t, tzinfo=LONDON)
            ev.add("dtstart", begin)
            ev.add("dtend", begin + VW_DEFAULT_LENGTH)
        else:
            ev.add("dtstart", date)
            ev.add("dtend", date + dt.timedelta(days=1))
        events.append(ev)

    print(f"Victoria Warehouse: {len(events)} events")
    return events


# ---------------------------------------------------------------- Man Utd home games

def is_home_game(ev):
    location = str(ev.get("location", "")).lower()
    if location:
        return "old trafford" in location
    # No location given: the home team is listed first, e.g. "Manchester United v Arsenal"
    summary = str(ev.get("summary", "")).lower()
    for sep in (" vs. ", " vs ", " v ", " - "):
        if sep in summary:
            home_side = summary.split(sep, 1)[0]
            return any(n in home_side for n in UNITED_NAMES)
    return False


def united_home_games(url):
    url = url.replace("webcal://", "https://", 1)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    source = Calendar.from_ical(r.content)

    games, timezones = [], []
    for comp in source.walk():
        if comp.name == "VTIMEZONE":
            timezones.append(comp)
        elif comp.name == "VEVENT" and is_home_game(comp):
            games.append(comp)
    print(f"Man Utd: {len(games)} home games")
    return games, timezones


# ---------------------------------------------------------------- Build feed

def main():
    vw = victoria_warehouse_events(env("TM_API_KEY"))
    games, timezones = united_home_games(env("MUFC_ICS_URL"))
    if not vw and not games:
        sys.exit("Both sources came back empty - keeping the existing calendar")

    cal = Calendar()
    cal.add("prodid", "-//Old Trafford area events//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "Old Trafford Events")
    cal.add("x-wr-timezone", "Europe/London")
    cal.add("refresh-interval", dt.timedelta(hours=6), parameters={"VALUE": "DURATION"})
    cal.add("x-published-ttl", "PT6H")

    seen_tz = set()
    for tz in timezones:
        tzid = str(tz.get("tzid"))
        if tzid not in seen_tz:
            seen_tz.add(tzid)
            cal.add_component(tz)
    for ev in vw + games:
        cal.add_component(ev)
    if hasattr(cal, "add_missing_timezones"):  # icalendar 6+: embed Europe/London definition
        cal.add_missing_timezones()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(cal.to_ical())
    print(f"Wrote {len(vw) + len(games)} events to {OUTPUT}")


if __name__ == "__main__":
    main()
