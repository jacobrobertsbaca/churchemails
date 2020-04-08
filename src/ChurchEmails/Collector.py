from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class collector:
    kGoogleMapsUrl = "https://www.google.com/maps/"
    kGoogleMapsSearchBarId = "searchboxinput"
    kGoogleMapsSearchResultClass = "section-result"
    kResultTitleElementClass = "section-result-title"
    kResultActionContainerElementClass = "section-result-action-container"
    kResultActionElementClass = "section-result-action"

    def __init__ (self):
        # Open a virtual browser instance
        self.driver = webdriver.Firefox();
        self.driver.set_page_load_timeout(5)

    def getByCity(self, city, state):
        print(f"Collecting church emails on {city}...")
        self.driver.get(self.kGoogleMapsUrl)
        searchbar = self.driver.find_element_by_id(self.kGoogleMapsSearchBarId)
        searchbar.clear()
        searchbar.send_keys(f"churches in {city}, {state}")
        searchbar.send_keys(Keys.RETURN)

        ## begin parsing through the search results
        time.sleep (5)
        resultElements = self.driver.find_elements_by_class_name(self.kGoogleMapsSearchResultClass)
        results = []
        print(f"Found {len(resultElements)} results for query 'churches in {city}, {state}'...")
        for element in resultElements:
            title = element.find_element_by_class_name(self.kResultTitleElementClass).find_element_by_xpath("./span").text
            url = element.find_element_by_class_name(self.kResultActionContainerElementClass).find_elements_by_xpath("./*")[0].find_element_by_class_name(self.kResultActionElementClass).get_attribute("href")

            print (f"Found church {title} at {url}.")
            results.append({
                "title": title,
                "url": url
            })
        
       
        sleep(10)

    def quit (self):
        self.driver.close()
