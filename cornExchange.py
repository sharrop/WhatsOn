from time import sleep
import re
import json
from datetime import datetime, timedelta, time
import uuid
import traceback
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vBinary


# Check existance of executable ChromeDriver
DRIVER='.\\chromedriver.exe'
if not os.path.exists(DRIVER):
    print(f'ERROR: ChromeDriver [{DRIVER}] not found')
    sys.exit(1)
if not os.path.isfile(DRIVER):
    print('ERROR: ChromeDriver [{DRIVER}] is not a file')
    sys.exit(1)
if not os.access(DRIVER, os.X_OK):
    print('ERROR: ChromeDriver [{DRIVER}] is not executable')
    sys.exit(1)

service = Service(DRIVER)
service.start()

driver = webdriver.Remote(service.service_url)
driver.get('https://cornexchangenew.com/all-events/');

# iCalendar library to generate an iCal (.ics) file
cal = Calendar()
cal.add('VERSION', '2.0')
cal.add('PRODID', '-//Newbury Corn Exchange//')
cal.add('X-WR-CALNAME', 'Newbury Corn Exchange')
cal.add('X-WR-TIMEZONE', 'Europe/London')
cal.add('X-WR-CALDESC', 'Events at The Newbury Corn Exchange')
cal.add('X-WR-RELCALTYPE', 'PUBLIC')
cal.add('X-WR-RELCALNAME', 'Newbury Corn Exchange')
cal.add('X-WR-RELCALURL', 'https://cornexchangenew.com/all-events/')
cal.add('X-WR-RELCALPRIV', 'PUBLIC')


listing_page = True
while listing_page:
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    listings = soup.find('ul', attrs = {'class': 'row listing__item__list small-up-1 medium-up-1'})
    for listing in listings:
        try:
            event = Event()
            # Generate a unique ID for each event
            event.add('UID', uuid.uuid4())           # Unique ID for the Event
            event.add('CREATED', datetime.now())     # When the Event was created
            event.add('DTSTAMP', datetime.now())     # When the Event was last modified

            item = listing.article
            subject_node = item.find('h2', attrs = {'class': 'listing__item__title'})
            if subject_node and subject_node.text:
                subject = subject_node.text
            else:
                subject = 'Not Stated'
            event.add('SUMMARY', subject)

            event_url = item.div.a.get("href")
            event_date_node = item.find('p', attrs = {'class': 'listing__item__date'})
            if event_date_node:
                event_date = event_date_node.text.strip()
                # Convert the event date to a date object from: "Friday 24th November 2023"
                # Strip 'th', 'rd', 'nd', 'st'from the date string, and convert to a date object.
                event_date = event_date.replace('th ', ' ')
                event_date = event_date.replace('st ', ' ') #TODO: Kills 'August'
                event_date = event_date.replace('rd ', ' ')
                event_date = event_date.replace('nd ', ' ')
                if '—' in event_date:
                    date_text = event_date.split('—')
                    start = date_text[0].strip()
                    end = date_text[1].strip()
                    print(f'** There is a date range stated for [{subject}] from [{start}] to [{end}] **')

                    captured_start_date = datetime.strptime(start, '%A %d %B %Y').date()
                    captured_end_date = datetime.strptime(end, '%A %d %B %Y').date()
                else:
                    print(f'** There is single date stated for [{subject}] at [{event_date}] **')
                    captured_start_date = captured_end_date = datetime.strptime(event_date, '%A %d %B %Y').date()
            else:
                raise Exception(f'No event date specified for [{subject}] -- skipping')

            venue_node = item.find('p', attrs = {'class': 'listing__item__venue'})
            if (venue_node):
                event_location = venue_node.text.strip()
            else:
                event_location = 'Not Stated'
            event.add('LOCATION', event_location)

            # Get the detailed event description for event time, date and price
            driver.get(event_url);
            event_soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = event_soup.find('h2', attrs = {'class': 'event__meta__tickets'})
            event_time_node = event_soup.find('a', attrs = {'data-tooltip-content': '#tooltip_content__1'})
            if (event_time_node):
                event_time = event_time_node.text.strip()
                print(f'** There is a time stated for [{subject}] on [{event_date}] at [{event_time}] **')
                # Remove all text beyond the am or pm from the time string
                event_time = re.sub(r'm.*$', 'm', event_time, flags=re.S)
                time_text = re.findall(r'\d{1,2}:\d\d', event_time)
                if time_text:
                    hours = time_text[0].split(':')[0]
                    if event_time.find('pm') != -1:
                        hours = int(hours) + 12
                    minutes = time_text[0].split(':')[1]
                    full_datetime = datetime.combine(
                        captured_start_date,
                        time(hour=int(hours), minute=int(minutes))
                        )
                else:
                    print(f'** Cannot parse a time from [{event_time}], so just using the date **')
                    # Don't have a time specified, so just use the start date
                    full_datetime = captured_start_date
                event.add('DTSTART', full_datetime)
                # Assume the event in 2 hours long
                event.add('DTEND', full_datetime + timedelta(hours=2))
            else:
                # Don't have a time specified, so just use the start date
                print(f'** Cannot parse a time from [{event_time}], so just using the date **')
                event.add('DTSTART', captured_start_date)
                event.add('DTEND', captured_start_date)

            price_text = price.text.strip()
            description = item.find('div', attrs = {'class': 'listing__item__summary'}).p.text
            
            if '/' in price_text:
                # There are multiple prices quoted
                price_text = price_text.split('/')
                prices = []
                for p in price_text:
                    prices.append(p.strip() + '\n')
                price_text = prices
            else:
                price_text = [price_text]

            full_description = f'Details: {event_url}\n\n{description}\n\nPrice: {price_text}'
            event.add('DESCRIPTION', f'{full_description}')

            # Add the event to the calendar
            # print(f'Adding New Event:\n{event}\n==========================================')
            cal.add_component(event)

        except Exception as e:
            print(f'**Problem parsing listing [{listing.prettify()}]: {e}: [{traceback.print_exc()}]')

        # Find more pages
        listing_page = soup.find('a', attrs = {'class': 'pagination__item ias-next btn btn--primary btn--small btn--next'})
        if listing_page:
            driver.get(listing_page.get('href'))

driver.quit()
print(f'Calendar [{cal.name}] has [{len(cal.items())}] entries')
ics_file = open('cornExchange.ics', 'wb')
ics_file.write(cal.to_ical())
ics_file.close()