# Old Trafford Events calendar

One auto-updating calendar with every O2 Victoria Warehouse event and every Manchester United home game. It updates daily on GitHub for free, and Alexa reads it out through two routines.

## 1. Get the two inputs

**Ticketmaster API key.** Sign up free at developer.ticketmaster.com, create an app, and copy the *Consumer Key*.

**Man Utd calendar link.** Go to manutd.com/en/team-fixture-calendars, find *Men's Team Fixtures*, and copy the calendar link (in the Outlook instructions, right-click the Men's Calendar link and choose "Copy link"). A link starting with `webcal://` is fine.

## 2. Set up the GitHub repo

1. Create a new **public** repository on github.com.
2. Upload these files, keeping the folder structure: `build_calendar.py`, `requirements.txt`, `.github/workflows/update-calendar.yml`.
3. Open **Settings → Secrets and variables → Actions → New repository secret** and add two secrets:
   - `TM_API_KEY` = your Ticketmaster key
   - `MUFC_ICS_URL` = the Man Utd calendar link
4. Open the **Actions** tab, choose *Update Old Trafford calendar*, and click **Run workflow**. After it finishes, a file appears at `docs/old-trafford.ics`.
5. Open **Settings → Pages**, set Source to *Deploy from a branch*, then pick branch `main` and folder `/docs`, and save.

Your calendar's address is:
`https://YOUR-USERNAME.github.io/YOUR-REPO/old-trafford.ics`

## 3. Subscribe to the calendar

- **Google:** on calendar.google.com, go to Other calendars → + → From URL, and paste the address.
- **Outlook.com:** go to Add calendar → Subscribe from web.
- **iPhone:** go to Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar.

Subscribe in an account that is linked to Alexa. Subscribed calendars refresh on the provider's schedule, which can take up to about a day with Google.

## 4. Set up Alexa

1. In the Alexa app, go to **Settings → Calendar**, open the linked account, and make sure *Old Trafford Events* is ticked. If it isn't listed, try subscribing in a different provider (Outlook or iCloud).
2. Go to **Routines → +** and create:
   - **Evening:** Schedule, every day at 20:00, with the action Calendar → *Tomorrow*
   - **Morning:** Schedule, every day at 07:00, with the action Calendar → *Today*

## Troubleshooting

- **The Actions run failed:** open it to read the error. Your existing calendar is never wiped by a failed run.
- **Victoria Warehouse shows 0 events:** some shows are sold through other ticket sites. Check the log for the venue the script found. If it picked the wrong one, set the right id as a repository *variable* called `TM_VENUE_ID`.
- **A home game is missing or an away game appears:** the filter uses the fixture's location ("Old Trafford"). If no location is given, it uses the team listed first. Adjust `is_home_game()` if the club changes its format.
