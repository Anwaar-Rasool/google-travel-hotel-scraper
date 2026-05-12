from playwright.sync_api import sync_playwright
import time


class TravelEssentials:
    def __init__(self):
        browser = sync_playwright().start()
        paly = browser.chromium.launch(headless=False)
        self.page = paly.new_page()

    def extract_single_element(self, selector, attribute='text', timeout=500):
        try:
            element = self.page.locator(selector).nth(0)
            element.wait_for(timeout=timeout)
            if attribute == 'text':
                return element.inner_text()
            elif attribute in ['innerHTML', 'href', 'src', 'value', 'aria-label']:
                return element.get_attribute(attribute)
            elif attribute == 'no':
                return element
        except Exception as e:
            print(e)
            return ""
        
    def extract_multiple_elements(self, selector, attribute='text', timeout=500):
        try:
            waiiter = self.page.wait_for_selector(selector=selector, timeout=timeout)
            elements = self.page.locator(selector=selector).all()
            if attribute == 'text':
                return [e.inner_text() for e in elements]
            elif attribute == 'no':
                return elements
            elif attribute in ['innerHTML', 'href', 'src', 'value', 'aria-label']:
                return [e.get_attribute(attribute) for e in elements]
        except:
            return []