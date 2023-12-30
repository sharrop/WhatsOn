import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
from datetime import datetime

service = Service('C:\\Users\\Steve\\Desktop\\dev\\WhatsOn\\chromedriver.exe')
service.start()

driver = webdriver.Remote(service.service_url)
#driver.get('https://cornexchangenew.com/events/');
driver.get('https://cornexchangenew.com/all-events/');
listing_page = True
while listing_page:
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    listings = soup.find('ul', attrs = {'class': 'row listing__item__list small-up-1 medium-up-1'})
    for listing in listings:
        try:
            event = {}
            item = listing.article
            div = item.div
            event_url = item.div.a.get("href")
            # Get the event description
            driver.get(event_url);
            event_soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = event_soup.find('h2', attrs = {'class': 'event__meta__tickets'})
            event_date = item.find('p', attrs = {'class': 'listing__item__date'}).text.strip()
            # Convert the event date to a date object from: "Friday 24th November 2023"
            # TODO: Need to deal with: "Wednesday 13th December 2023 — Tuesday 2nd January 2024"
            # Strip 'th', 'rd', 'nd', 'st'from the date string, and convert to a date object.
            event_date = event_date.replace('th ', ' ')
            event_date = event_date.replace('st ', ' ')
            event_date = event_date.replace('rd ', ' ')
            event_date = event_date.replace('nd ', ' ')
            if '—' in event_date:
                date_text = event_date.split('—')
                start_date = date_text[0].strip()
                end_date = date_text[1].strip()
                # print(f'Parsing dates [{date_text}]: start [{start_date}], end [{end_date}]')
                start = datetime.strptime(start_date, '%A %d %B %Y').date()
                end = datetime.strptime(end_date, '%A %d %B %Y').date()
                dates = {
                    'from': str(start),
                    'until': str(end)
                }
            else:
                dates = str(datetime.strptime(event_date, '%A %d %B %Y').date())

            price_text = price.text.strip()
            # TODO: Need to deal with: "£10.00"
            # price_text = price_text.replace('\u00a3', '£')
            
            if '/' in price_text:
                price_text = price_text.split('/')
                prices = []
                for p in price_text:
                    prices.append(p.strip())
                price_text = prices
            else:
                price_text = [price_text]

            event = {
                'title': item.find('h2', attrs = {'class': 'listing__item__title'}).text,
                'summary': item.find('div', attrs = {'class': 'listing__item__summary'}).p.text,
                'link': event_url,
                'venue': item.find("p", attrs = {"class": "listing__item__venue"}).text.strip(),
                'date': dates,
                'price': price_text
            }
        except Exception as e:
            print(f'Problem parsing listing [{listing}]: {e}')
            event = {}

        print(json.dumps(event, indent = 2))
        print(f'\n================\n')

        # Find more pages
        listing_page = soup.find('a', attrs = {'class': 'pagination__item ias-next btn btn--primary btn--small btn--next'})
        if listing_page:
            driver.get(listing_page.get('href'))
            #page = driver.page_source
            #soup = BeautifulSoup(page, 'html.parser')

# time.sleep(1) # Let the user actually see something!

driver.quit()
