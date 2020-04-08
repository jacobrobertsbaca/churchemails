from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
import socket
import time
import re
import requests
from urllib.parse import urlsplit
import tldextract
import signal

class collector:
    kGoogleMapsUrl = "https://www.google.com/maps/"
    kGoogleMapsSearchBarId = "searchboxinput"
    kGoogleMapsSearchResultClass = "section-result"
    kResultTitleElementClass = "section-result-title"
    kResultActionContainerElementClass = "section-result-action-container"
    kResultActionElementClass = "section-result-action"
    kResultDetailsContainerClass = "section-result-details-container"
    kResultDetailsRoleClass = "section-result-details"
    kResultDetailsLocationClass = "section-result-location"

    kEmailRegex = '[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+'
    kEmailInvalidBoundingCharacters = ("!", "#", "$", "%", "&", "'", "*", "+", "-", "/", "=", "?", "^", "_", "`", "{", "|", '"', "(", ")", ",", ":", ";", "<", ">", "@", "[", "\\", "]" )

    kRequestHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

    def __init__ (self):
        # Open a virtual browser instance
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)

        self.driver.set_page_load_timeout(5)

    def _raise(ex):
        raise ex

    def connected(self, host="8.8.8.8", port=53, timeout=3):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            print(ex)   
        return False

    def getByCity(self, city, state):
        # check if connected
        if (not self.connected()):
            raise ConnectionError("Not connected")

        # caller did not pass in city or state
        if (not city or not state): return
        print(f"\n\n-------SEARCHING CHURCHES IN {city.upper()}, {state.upper()}-------")
        self.driver.get(self.kGoogleMapsUrl)
        searchbar = self.driver.find_element_by_id(self.kGoogleMapsSearchBarId)
        searchbar.clear()
        searchbar.send_keys(f"churches in {city}, {state}")
        searchbar.send_keys(Keys.RETURN)

        # wait for search results to become available
        try:
            secondsDelay = 20 # max number of seconds to delay before continuing
            WebDriverWait(self.driver, secondsDelay).until(EC.presence_of_element_located((By.CLASS_NAME, self.kGoogleMapsSearchResultClass)))
        except TimeoutException:
            print("Search results did not load in time... May fail to collect data from this city.")

        ## begin parsing through the search results
        time.sleep (5)
        resultElements = self.driver.find_elements_by_class_name(self.kGoogleMapsSearchResultClass)
        if (len(resultElements) == 0): return []
        results = []
        print(f"Found {len(resultElements)} results for query 'churches in {city}, {state}'...")
        for element in resultElements:
            title = element.find_element_by_class_name(self.kResultTitleElementClass).find_element_by_xpath("./span").text
            url = element.find_element_by_class_name(self.kResultActionContainerElementClass).find_elements_by_xpath("./*")[0].find_element_by_class_name(self.kResultActionElementClass).get_attribute("href")
            details = element.find_element_by_class_name(self.kResultDetailsContainerClass)
            role = details.find_element_by_class_name(self.kResultDetailsRoleClass).text
            location = details.find_element_by_class_name(self.kResultDetailsLocationClass).text

            print (f"Found church {title} at {url} of type '{role}'.")
            results.append({
                "title": title,
                "url": url,
                "type": role,
                "location": location
            })

        # Now that we have found some websites, we need to go through each of them and scrape off any emails we can find
        success = []
        for result in results:
            if not result["url"]: continue
            urlparts = urlsplit(result["url"])
            url = result["url"]
            # get HTTP raw response

            try:
                start = time.clock()
                print(f"Getting raw html from '{url}'... ", end='')
                response = requests.get(url, headers=self.kRequestHeaders, timeout=(10,5))
            except:
                print(f"failed.")
                continue
            if (not response.ok):
                print(f"failed.")
                continue
            else: print(f"took {(time.clock() - start) * 1000} ms")

            start = time.clock()
            print(f"Scraping '{url}' for emails... ", end='')
            potentialEmails = set(re.findall(self.kEmailRegex, response.text, re.I))
            print(f"took {(time.clock() - start) * 1000} ms")
            emails = [] # find processed emails list

            for email in potentialEmails:
                # Do not allow invalid emails that start or end with a bad character
                if email.startswith(self.kEmailInvalidBoundingCharacters) or email.endswith(self.kEmailInvalidBoundingCharacters): continue
                # Do not allow emails that have a non-standard domain extension
                if not tldextract.extract(email).suffix: continue
                emails.append(email)
                print (f"Found: '{email}'")

            if (len(emails) == 0): continue # no emails, don't record this entry
            result["emails"] = emails
            success.append(result)

        return success

    def quit (self):
        self.driver.close()
