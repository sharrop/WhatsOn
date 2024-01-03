# WhatsOn
Scanning various event websites to compile a list of what's on, where, and when in the Newbury area. This uses [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/#stable) to navigate the pages, and [Beautiful Soup](https://en.wikipedia.org/wiki/Beautiful_Soup_(HTML_parser)) to parse the HTML, then the [iCalendar](https://pypi.org/project/icalendar/) Python library to form an [RFC5545](https://www.ietf.org/rfc/rfc5545.txt) compliant calendar file (.ics) that can be imported or linked to from Outlook, Google Calendar etc.

Ultimately I intend to:
1. Cover many event venues in/around my area
2. Host the resutlant ICS files for linking to calendars (GitHub, or S3)
3. Build a robust pipeline to periodically build, validate and release the ICS files

## Venues
Venues and their event websites that I have in mind include:

| Venue      | Website | First Attempt |
| ----------- | ----------- | ----------- |
| Corn Exchange      | https://cornexchangenew.com/events/ |  |
| Arlington Arts Centre   | https://arlingtonarts.ticketsolve.com/ticketbooth/shows?i=64 | [arlington.ics](https://github.com/sharrop/WhatsOn/blob/main/arlington.ics) |
| Ace Space | https://acespace.org.uk/events/ | |
| The WaterMill | https://www.watermill.org.uk/ | |
| Shaw House | https://booking.westberks.gov.uk/heritage_events.html | |
| The Mount, Wasing | https://www.wasing.co.uk/events/ | |
| Welford Park | https://www.welfordpark.co.uk/events/ | |
| Highclere Castle | https://www.highclerecastle.co.uk/events/ | |

### Prerequisites

Requirements for the software and other tools to build, test and push 
- Download the [latest ChromeDriver executable](https://googlechromelabs.github.io/chrome-for-testing/#stable) for your platform
- Download/Fork this repo
- Pip Install the requirements (sorry - no requirements.txt yet)
- In these early days I am just writing bespoke ***place***.py files that individually generate a ***place***.ics file. Each can be invoked with:

```sh
python arlington.py
```
