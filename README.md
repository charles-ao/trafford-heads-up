# Old Trafford Events calendar

One auto-updating calendar with every O2 Victoria Warehouse event and every Manchester United home game. It updates daily on GitHub for free, and Alexa reads it out through routines.

## 1. Get the two inputs

**Ticketmaster API key.** Sign up free at developer.ticketmaster.com, create an app, and copy the *Consumer Key*.

**Man Utd calendar link.** Go to manutd.com/en/team-fixture-calendars, find *Men's Team Fixtures*, and copy the calendar link (in the Outlook instructions, right-click the Men's Calendar link and choose "Copy link"). A link starting with `webcal://` is fine.

## 2. The GitHub repo

1. Clone repository on github.com.
2. Open **Settings → Secrets and variables → Actions → New repository secret** and add two secrets:
   - `TM_API_KEY` = your Ticketmaster key
   - `MUFC_ICS_URL` = the Man Utd calendar link
3. Open the **Actions** tab, choose *Update Old Trafford calendar*, and click **Run workflow**. After it finishes, a file appears at `docs/old-trafford.ics`.
4. Open **Settings → Pages**, set Source to *Deploy from a branch*, then pick branch `main` and folder `/docs`, and save.

Your calendar's address is:
`https://YOUR-USERNAME.github.io/YOUR-REPO/old-trafford.ics`

## 3. Subscribe to the calendar

- **Google:** on calendar.google.com, go to Other calendars → + → From URL, and paste the address.
- **Outlook.com:** go to Add calendar → Subscribe from web.
- **iPhone:** go to Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar.

Subscribe in an account that is linked to Alexa. Subscribed calendars refresh on the provider's schedule, which can take up to about a day with Google.

## 4. Set up Alexa

1. In the Alexa app, go to **Settings → Calendar**, open the linked account, and make sure *Old Trafford Events* is ticked. If it isn't listed, try subscribing in a different provider (Outlook or iCloud).
2. Go to **Routines → +** and create preferred routine.