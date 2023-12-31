import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

service = Service('C:\\Users\\Steve\\Desktop\\dev\\WhatsOn\\chromedriver.exe')
service.start()

driver = webdriver.Remote(service.service_url)
driver.get('https://cornexchangenew.com/all-events/');

# Open an output file to write the details as a CSV file
out_file = open('events.csv', 'w')

# Write the header row to the CSV file
out_file.write('Subject,Start Date,Start Time,End Date,All Day Event,Description,Location,Private\n')

listing_page = True
while listing_page:
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    listings = soup.find('ul', attrs = {'class': 'row listing__item__list small-up-1 medium-up-1'})
    for listing in listings:
        try:
            item = listing.article
#            div = item.div
            subject = item.find('h2', attrs = {'class': 'listing__item__title'}).text
            event_url = item.div.a.get("href")
            event_date = item.find('p', attrs = {'class': 'listing__item__date'}).text.strip()
            venue = item.find('p', attrs = {'class': 'listing__item__venue'})
            if (venue):
                event_location = venue.text.strip()
            else:
                event_location = 'Not Stated'

            # Get the detailed event description for event time, date and price
            driver.get(event_url);
            event_soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = event_soup.find('h2', attrs = {'class': 'event__meta__tickets'})
            event_time = event_soup.find('a', attrs = {'data-tooltip-content': '#tooltip_content__1'}).text.strip()
            # Remove all text beyond the am or pm from the time string
            event_time = re.sub(r'm.*$', 'm', event_time, flags=re.S)
            event_time = event_time.replace('am', ' AM')
            event_time = event_time.replace('pm', ' PM')

            # Convert the event date to a date object from: "Friday 24th November 2023"
            # TODO: Need to deal with: "Wednesday 13th December 2023 — Tuesday 2nd January 2024"
            # Strip 'th', 'rd', 'nd', 'st'from the date string, and convert to a date object.
            event_date = event_date.replace('th ', ' ')
            event_date = event_date.replace('st ', ' ')
            event_date = event_date.replace('rd ', ' ')
            event_date = event_date.replace('nd ', ' ')
            if '—' in event_date:
                date_text = event_date.split('—')
                start = date_text[0].strip()
                end = date_text[1].strip()
                # Need to put these in the format: 05/30/2020
                captured_start_date = datetime.strptime(start, '%A %d %B %Y').date()
                start_date = captured_start_date.strftime('%m/%d/%Y')
                captured_end_date = datetime.strptime(end, '%A %d %B %Y').date()
                end_date = captured_end_date.strftime('%m/%d/%Y')
            else:
                captured_date = str(datetime.strptime(event_date, '%A %d %B %Y').date())
                start_date = captured_date
                end_date = captured_date

            price_text = price.text.strip()
            description = item.find('div', attrs = {'class': 'listing__item__summary'}).p.text
            
            if '/' in price_text:
                # There are multiple prices quoted
                price_text = price_text.split('/')
                prices = []
                for p in price_text:
                    prices.append(p.strip())
                price_text = prices
            else:
                price_text = [price_text]

            full_description = f'{description}\\nPrice: {price_text}\\nDetails: {event_url} \\n\\nRecorded at {datetime.now()}'
            line_item = f'"{subject}",{start_date},{event_time},{end_date},False,"{full_description}","{event_location}",False'
            out_file.write(line_item + '\n')
            print(line_item)

        except Exception as e:
            print(f'Problem parsing listing [{listing}]: {e}')

        # Find more pages
        listing_page = soup.find('a', attrs = {'class': 'pagination__item ias-next btn btn--primary btn--small btn--next'})
        if listing_page:
            driver.get(listing_page.get('href'))

out_file.close()
driver.quit()
