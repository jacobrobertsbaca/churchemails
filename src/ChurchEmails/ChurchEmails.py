import Collector
import DataAggregator
from tkinter import Tk, filedialog
import easygui
import os
import csv

def collectAndStore(aggregator, collector, blacklist=[]):
    # First let user choose where they want to store bulk of data
    root = Tk()
    root.withdraw()
    storePath = filedialog.askdirectory()
    if (not storePath): raise ValueError ("Select a folder to store files")
    
    # Go through each state and go through each city and begin to collect data,
    # storing it into csv as we go
    for state, cities in aggregator.byState.items():
        # Don't search in state if this stae is in the blacklist
        if (state in blacklist): continue

        # Create state directory
        statePath = os.path.join(storePath, state)
        if (not os.path.isdir(statePath)): os.mkdir(statePath)

        # go through cities
        for city in cities:
            # open city file
            cityPath = os.path.join(statePath, city["city"]) + ".csv"
            if (os.path.isfile(cityPath)): os.remove(cityPath)
            with open(cityPath, mode='w', newline='') as city_file:
                csvWriter = csv.writer(city_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                # write headers
                csvWriter.writerow(["name", "location", "type", "url", "email"])
                # collect info
                results = collector.getByCity(city["city"], state)
                if (len(results) == 0): continue
                for result in results:
                    for email in result["emails"]:
                        csvWriter.writerow([
                            result["title"],
                            result["location"],
                            result["type"],
                            result["url"],
                            email
                        ])

def getBlacklist():
    path = easygui.fileopenbox("Select optional blacklist file", None, "*", "*.txt")
    if (not path): return []
    with open(path, mode='r') as file:
        entries = file.read().split(',')
        for i in range(len(entries)):
            entries[i] = entries[i].lower().strip()
        return entries

def main():
    print("-------USA CHURCH EMAILS FINDER-------")
    print("Written by rbjacob101\n")
    threshold = int(input("Please enter the minimum population to consider when searching for churches in cities (an integer):"))

    print("Please select a path to the csv file containing the USA cities information...")
    aggregator = DataAggregator.aggregator(threshold)
    aggregator.begin()
    print(f"Only considering cities with at least {threshold} people")
    print(f"Number of cities found with at least {threshold} people: {len(aggregator.dataset)}")
    print(f"Number of states registered: {len(aggregator.byState)}")

    print("Select a file containing a list of comma-seperated entries with states that should not be searched (optional)")
    blacklist = getBlacklist()

    print("Opening browser marionette... This can take a few moments...")
    col = Collector.collector()
    print("Please select a path to a folder where the raw data will be stored...")
    collectAndStore(aggregator, col, blacklist)



main()