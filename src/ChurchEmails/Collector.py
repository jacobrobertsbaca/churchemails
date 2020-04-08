from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import requests
from urllib.parse import urlsplit
import tldextract

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

    kEmailRegex = '(?:[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    kEmailInvalidBoundingCharacters = ("!", "#", "$", "%", "&", "'", "*", "+", "-", "/", "=", "?", "^", "_", "`", "{", "|", '"', "(", ")", ",", ":", ";", "<", ">", "@", "[", "\\", "]" )

    def __init__ (self):
        # Open a virtual browser instance
        self.driver = webdriver.Firefox();
        self.driver.set_page_load_timeout(5)

    def getByCity(self, city, state):
        # caller did not pass in city or state
        if (not city or not state): return
        print(f"\n\n-------SEARCHING CHURCHES IN {city.upper()}, {state.upper()}-------")
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
            url = f"{urlparts.scheme}://{urlparts.netloc}{urlparts.path}"
            print(f"Scraping '{url}' for emails.")
            # get HTTP raw response
            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                continue
            if (not response.ok): continue

            potentialEmails = set(re.findall(self.kEmailRegex, response.text, re.I))
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


        sleep(10)

    def quit (self):
        self.driver.close()
