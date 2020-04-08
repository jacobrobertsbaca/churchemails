import easygui
import csv
from collections import defaultdict

class aggregator:

    kCityNameHeader = "city"
    kStateNameHeader = "state_name"
    kPopulationHeader = "population"

    def __init__(self, populationThreshold):
        self.popThreshold = populationThreshold

    def _readdata(self):
        self.dataset = []

        with open(self.datasetPath, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            line_count = 0

            cityColumnIndex = 0
            stateColumnIndex = 0
            populationColumnIndex = 0

            for row in csv_reader:
                if (line_count == 0):
                    for i in range(len(row)):
                        if (row[i] == self.kCityNameHeader): cityColumnIndex = i
                        elif (row[i] == self.kStateNameHeader): stateColumnIndex = i
                        elif (row[i] == self.kPopulationHeader): populationColumnIndex = i
                else:
                    # reading a city entry in csv
                    # if population is greater than the population threshold, log this city into the dataset
                    if (float(row[populationColumnIndex]) < self.popThreshold): continue
                    self.dataset.append({
                        "city": row[cityColumnIndex].lower().strip(),
                        "state": row[stateColumnIndex].lower().strip(),
                        "population": row[populationColumnIndex]
                        })
                line_count += 1

            self.byState = defaultdict(list)
            for city in self.dataset:
                self.byState[city['state']].append(city)

    def begin(self):
        self.datasetPath = easygui.fileopenbox("Select cities dataset", "Select cities CSV", "*.csv", False)
        if (not self.datasetPath): raise ValueError("Select a valid path to CSV dataset")
        self._readdata()
