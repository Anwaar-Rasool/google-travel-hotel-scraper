from playwright.sync_api import sync_playwright
from threading import Thread
import pandas as pd 
import re
import os
import time


class PlaywrightAssistantClass:
    def __init__(self, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.links = []

    def navigate(self, url):
        self.page.goto(url)
        self.page.evaluate('document.body.style.zoom="25%"')

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
    
    def extract_single_element(self, selector, timeout=500, attr='text'):
        try:
            element = self.page.locator(selector).first
            if attr == 'text':
                return element.text_content(timeout=timeout)
            else:
                return element.get_attribute(attr, timeout=timeout)
        except:
            return ""
    
    def extract_multiple_elements(self, selector, timeout=500, attr='text'):
        try:
            elements = self.page.locator(selector).all()
            results = []
            for element in elements:
                if attr == 'text':
                    results.append(element.text_content(timeout=timeout))
                else:
                    results.append(element.get_attribute(attr, timeout=timeout))
            return results
        except Exception as e:
            print(e)
            return []
    
    def click_on_btn(self, selector, timeout=500):
        try:
            element = self.page.locator(selector).first
            element.click(timeout=timeout)
        except:
            print(f"Could not click on button: {selector}")
    
    def save_into_file(self, df, city):
        os.makedirs('./city_wise_data', exist_ok=True)
        p = pd.DataFrame([df])
        p.to_csv(f'./city_wise_data/{city}.csv', mode='a', index=False, header=not os.path.exists(f'./city_wise_data/{city}.csv'), encoding='utf-8-sig')
        p.to_csv(f'./Tanzania.csv', mode='a', index=False, header=not os.path.exists(f'./Tanzania.csv'), encoding='utf-8-sig')



class GoogleTravelLinkScraper(PlaywrightAssistantClass):
    def __init__(self):
        PlaywrightAssistantClass.__init__(self, headless=False)
        
    def handle_pagination(self):
        self.page.click('//span[@jsname="V67aGc" and text() = "Next"]', timeout=6000)

    def extract_listing_links(self):
        listing_links = self.extract_multiple_elements('//div[@jscontroller="rqWJpd"]/a', attr='href')
        listing_links = ["https://www.google.com"+link for link in listing_links if link]
        self.links.extend(listing_links)
        


class GoogleTravelDataScraper(GoogleTravelLinkScraper):
    def __init__(self):
        GoogleTravelLinkScraper.__init__(self)

    def extract_data_points(self, listing_url, target_city):
        title = self.extract_single_element('//div[@class="OLSp3e"]/h1', timeout=3000)
        estimated_price = self.extract_single_element('//span[@class="qQOQpe ERGPc prxS3d" or @class="qQOQpe prxS3d"]')
        review_count = self.extract_single_element('//div[@class="OGAsq" or @class="bNi4fd "]//span[contains(@aria-label, "stars from")]', attr='aria-label')
        rating = review_count.split(' ')[0] if review_count else ""
        reviews = review_count.split(' ')[-2].replace(',', '') if review_count else ""
        website = self.extract_single_element('//a[contains(@aria-label, "Visit site for ")]', attr='href')
        sleep = self.extract_single_element('//div[@class="hwR8Dd"]//span[contains(text(), "Sleeps")]').split(' ')[-1]
        bedroom_count = self.extract_single_element('//div[@class="hwR8Dd"]//span[contains(text(), "bedrooms")]').split(' ')[0]
        bathroom_count = self.extract_single_element('//div[@class="hwR8Dd"]//span[contains(text(), "bathroom")]').split(' ')[0]
        bed_count = self.extract_single_element('//div[@class="hwR8Dd"]//span[contains(text(), "beds")]').split(' ')[0]
        property_size = self.extract_single_element('//div[@class="hwR8Dd"]//span[contains(text(), "sq m")]').split(' ')[0]
        self.click_on_btn('(//div[@aria-label="Photos"])[1]', timeout=5000)
        time.sleep(1)
        images = self.extract_multiple_elements('//div[@class="QbNsGc"]//img', attr='src')
        images = ', '.join(["https:"+img.split('=')[0] for img in images if img])
        self.click_on_btn('(//div[@aria-label="About"])[1]', timeout=5000)
        time.sleep(1)
        address = self.extract_single_element('//span[contains(@aria-label, "hotel address is")]', attr='aria-label').removeprefix('hotel address is ')
        phone = self.extract_single_element('//span[contains(@aria-label, "call this hotel: ")]', attr='aria-label').removeprefix('call this hotel: ')
        direction = self.extract_single_element('(//a[@aria-label="Directions"])[2]', attr='href')
        description = self.extract_single_element('(//section[@class="O3oTUb"])[1]')
        check_in = self.extract_single_element('//div[contains(text(), "Check-in time: ")]').split(': ')[-1]
        check_out = self.extract_single_element('//div[contains(text(), "Check-out time: ")]').split(': ')[-1]
        amenities = ', '.join(self.extract_multiple_elements('//div[div/h2[text() = "Amenities"]]//span[@class="veMtCf"]/span/span'))
        if not amenities:
            amenities = self.extract_multiple_elements('//li[@class="IXICF"]//span[@class="LtjZ2d"]')
            amenities = [am for am in amenities if not am.startswith('No')]
            amenities = ', '.join(amenities)
        varifications = ', '.join(self.extract_multiple_elements('//div[div/h2[text() = "Verifications"]]//span[@class="veMtCf"]/span/span'))
        other_sources = ', '.join(self.extract_multiple_elements('//a[@class="XZu2Vd kXgdre"]', attr='href'))

        data = {
            "Target City": target_city,
            "Title": title,
            "Address": address,
            "Phone": phone,
            "website": website,
            "Direction": direction,
            "Estimated Price": estimated_price,
            "Rating": rating,
            "Reviews": reviews,
            "Sleeps": sleep,
            "Bedrooms": bedroom_count,
            "Bathrooms": bathroom_count,
            "Beds": bed_count,
            "Property Size (sq m)": property_size,
            "Images": images,
            "Description": description,
            "Check-in": check_in,
            "Check-out": check_out,
            "Amenities": amenities,
            "Verifications": varifications,
            "Other Sources": other_sources,
            "Listing URL": listing_url
        }
        return data




def handle_multi_threading(target_city, url):
    bot = GoogleTravelDataScraper()
    bot.navigate(url)
    while True:
        bot.extract_listing_links()
        try:
            time.sleep(2)
            bot.handle_pagination()
            time.sleep(3)
        except:
            break
    print(f"Total links extracted: {len(bot.links)} for city: {target_city}")
    print("\n\n"+"="*50+"\n\n")
    for l in bot.links:
        bot.navigate(l)
        data = bot.extract_data_points(l, target_city)
        for key, value in data.items():
            print(f"{key}: {value}")
        print("\n"+"-"*50+"\n")
        bot.save_into_file(data, target_city)



url1 = "https://www.google.com/travel/search?q=hotels%20in%20Morogoro%20tanzania&ts=CAESCgoCCAMKAggDEAAqBwoFOgNVU0Q&ved=0CAAQ5JsGahgKEwjYi-q8krCSAxUAAAAAHQAAAAAQ1AM&ictx=3&authuser=0&qs=CAAgACgA&ap=MAA"
url2 = "https://www.google.com/travel/search?q=hotels%20in%20Tanga%20tanzania&ts=CAESCgoCCAMKAggDEAAqBwoFOgNVU0Q&ved=0CAAQ5JsGahgKEwjYi-q8krCSAxUAAAAAHQAAAAAQhQQ&ictx=3&authuser=0&qs=CAAgACgA&ap=MAA"
url3 = 'https://www.google.com/travel/search?q=hotels%20in%20Bagamoyo%20tanzania&ts=CAESCgoCCAMKAggDEAAaUwo1EjEyJTB4MTg1YzkxN2M5MTEwNzA1MzoweGFhMTc5ZmQ4OWNjNzY3MTQ6CEJhZ2Ftb3lvGgASGhIUCgcI6g8QAhgFEgcI6g8QAhgIGAMyAggCKgkKBToDVVNEGgA&ved=0CAAQ5JsGahgKEwjYi-q8krCSAxUAAAAAHQAAAAAQtgQ&ictx=3&authuser=0&qs=CAEgACgAOA1IAA&ap=MAE'
url4 = "https://www.google.com/travel/search?q=hotels%20in%20Kigoma%20tanzania&ts=CAESCgoCCAMKAggDEAAqCQoFOgNVU0QaAA&ved=0CAAQ5JsGahgKEwjYi-q8krCSAxUAAAAAHQAAAAAQoQY&ictx=3&authuser=0&qs=CAAgACgA&ap=MAA"
url5 = "https://www.google.com/travel/search?q=hotels%20in%20Tabora%20tanzania&ts=CAESCgoCCAMKAggDEAAqCQoFOgNVU0QaAA&ved=0CAAQ5JsGahgKEwjYi-q8krCSAxUAAAAAHQAAAAAQzwY&ictx=3&authuser=0&qs=CAAgACgA&ap=MAA"

th1 = Thread(target=handle_multi_threading, args=("Morogoro", url1))
th1.start()
time.sleep(10)

th2 = Thread(target=handle_multi_threading, args=("Tanga", url2))
th2.start()
time.sleep(10)

th3 = Thread(target=handle_multi_threading, args=("Bagamoyo", url3))
th3.start()
time.sleep(10)

th4 = Thread(target=handle_multi_threading, args=("Kigoma", url4))
th4.start()
time.sleep(10)

th5 = Thread(target=handle_multi_threading, args=("Tabora", url5))
th5.start()

th1.join()
th2.join()
th3.join()
th4.join()
th5.join()
