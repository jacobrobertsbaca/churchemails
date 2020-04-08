from tkinter import Tk, filedialog
import os
import os.path
import csv

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def main():
    print("-------USA CHURCH EMAILS AGGREGATOR-------")
    print("Written by rbjacob101\n")

    print("Please select the directory where the original data was stored to:")
    root = Tk()
    root.withdraw()
    originalPath = filedialog.askdirectory()
    if (not originalPath): raise ValueError("Select data directory.")
    print()

    print("Please select the directory where the batched emails should be stored to:")
    batchPath = filedialog.askdirectory();
    if (not batchPath): raise ValueError("Select batch directory")
    print()

    if (originalPath == batchPath): raise ValueError("Data path and batch path cannot be the same directory")

    emails = []
    for stateDir in listdir_fullpath(originalPath):
        if (os.path.isfile(stateDir)): continue
        for cityCsv in listdir_fullpath(stateDir):
            if (os.path.isdir(cityCsv)): continue # strip directories from query
            splitext = os.path.splitext(cityCsv)
            if (splitext[len(splitext) - 1].lower() != ".csv"): continue # strip non-csv from query

            with open(cityCsv, mode='r') as city_file:
                csv_reader = csv.reader(city_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                row_count = 0
                for row in csv_reader:
                    if (row_count != 0 and len(row) >= 5):
                        emails.append(row[4]) # we know that the email is stored at this particular position, however this could be written more explicitly
                    row_count += 1
        
    print(f"Found {len(emails)} emails")
main()