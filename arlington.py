import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
from datetime import datetime
from datetime import time
import re
from icalendar import Calendar, Event, vBinary
import uuid

from time import sleep
import urllib
from datetime import timedelta

service = Service('C:\\Users\\Steve\\Desktop\\dev\\WhatsOn\\chromedriver.exe')
service.start()

driver = webdriver.Remote(service.service_url)
HOST='https://arlingtonarts.ticketsolve.com'
driver.get('https://arlingtonarts.ticketsolve.com/ticketbooth/shows?i=64')
sleep(5)
page = driver.page_source
soup = BeautifulSoup(page, 'html.parser')

# iCalendar library to generate an iCal (.ics) file
cal = Calendar()
cal.add('VERSION', '2.0')
cal.add('PRODID', '-//Arlington Arts Centre//')
cal.add('X-WR-CALNAME', 'Arlington Arts')
cal.add('X-WR-TIMEZONE', 'Europe/London')
cal.add('X-WR-CALDESC', 'Events at Arlington Arts')
cal.add('X-WR-RELCALTYPE', 'PUBLIC')
cal.add('X-WR-RELCALNAME', 'Arlington Arts')
cal.add('X-WR-RELCALURL', 'https://arlingtonarts.ticketsolve.com/')
cal.add('X-WR-RELCALPRIV', 'PUBLIC')

listings = soup.find_all('article', attrs = {'class': 'show-card'})
for listing in listings:
    event = Event()
    # Generate a unique ID for each event
    event.add('UID', uuid.uuid4())           # Unique ID for the Event
    event.add('CREATED', datetime.now())     # When the Event was created
    event.add('DTSTAMP', datetime.now())     # When the Event was last modified

    subject_node = listing.find('h2')
    if subject_node:
        subject = subject_node.text
    else:
        subject = 'Not Stated'
    event.add('SUMMARY', subject)

    date_node = listing.find('span', attrs = {'class': 'truncate'})
    if date_node:
        date = date_node.text
        # Set the event date and start time later (if start time is known in the details page)  
    else:
        raise Exception(f'No event date specified for [{subject}] -- skipping')

    venue_node = listing.find('div', attrs = {'class': 'flex-grow truncate'})
    if venue_node and venue_node.text:
        venue = venue_node.text.strip()
    else:
        venue = "Venue Not Known"
    event.add('LOCATION', venue)

    # Get the detailed event description from the specific event page
    event_url = listing.a.get("href")
    event.add('URL', f'{HOST}{event_url}')
    description = f'Details Page: {HOST}{event_url}\n\n'

    driver.get(f'{HOST}{event_url}')
    # This page takes a moment to load fully - would be nice to have some notification of load-complete
    sleep(1)
    event_soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_node = event_soup.find('img', attrs = {'alt': 'cover'})
    if image_node:
        image_url = image_node.get('src')
        event.add('IMAGE', image_url)       # Does not seem to do anything

    """
        # Read the image data and add it to the event
        print(f'Reading image file [{image_url}]')
        request = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request) as image_file:
        image_data = image_file.read()
            attachment = vBinary(image_data)
        event.add( 'ATTACH', attachment, parameters = { 'FMTTYPE': 'image/jpeg', 'ENCODING': 'BASE64', 'VALUE': 'BINARY' } )  
    """
    # Get the detailed event description from the specific event page
    description_node = event_soup.find('div', attrs = {'class': 'overflow-hidden max-h-60 cursor-pointer default-style'})
    if description_node and description_node.div:
        description_node = description_node.div
        sections = description_node.find_all()
        full_text = ''
        for element in sections:
            if element.text:
                full_text += element.text
        description += full_text.strip()
    else:
        description += f'No detailed description found [{description_node}] for [{subject}]'
    event.add('DESCRIPTION', f'{description}')

    # Get the start time and add to the previous date
    event_time_node = event_soup.find('span', attrs = {'class': 'pl-1'})
    if event_time_node and event_time_node.text:
        # Likely to be in the form: "(Doors open 19:00)"
        time_text = re.findall(r'\d\d:\d\d', event_time_node.text)
        if time_text:
            hours = time_text[0].split(':')[0]
            minutes = time_text[0].split(':')[1]
            full_datetime = datetime.combine(
                datetime.strptime(date, '%d %b %Y'),
                time(hour=int(hours), minute=int(minutes))
                )
            event.add('DTSTART', full_datetime)
            # Assume the start time is 30mins before the event, and the event in 2 hours long
            event.add('DTEND', full_datetime + timedelta(hours=2, minutes=30))
    else:
        date_obj = datetime.strptime(date, '%d %b %Y')
        print(f'No event time found for [{subject}] on [{date_obj}]')
        # Just add the date to the event
        event.add('DTSTART', date_obj)
        event.add('DTEND', date_obj)

    # Add the event to the calendar
    cal.add_component(event)

driver.execute_script("window.scrollTo({ top: 1000, left: 0, behavior: 'smooth'});")
sleep(5)

driver.quit()

ics_file = open('arlington.ics', 'wb')
ics_file.write(cal.to_ical())
ics_file.close()