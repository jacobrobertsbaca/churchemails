from tkinter import Tk, filedialog
import os
import os.path
import csv
from collections import defaultdict
import random

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def write_batch(batchPath, batchNumber, emails):
    with open(os.path.join(batchPath, f"batch_{batchNumber}.txt"), mode='w+') as batch_file:
        batch_file.write('; '.join(emails))
        print (f"Batched {len(emails)} emails to {batch_file.name}")
    emails.clear()

def batch(batchPath, emails):
    max_batch = 200
    batch_number = 0
    emailsBuffer = []
    while (len(emails) > 0):
        index = random.randint(0, len(emails)-1)
        email = emails[index]
        del emails[index]
        emailsBuffer.append(email)
        if (len(emailsBuffer) == 200):
            write_batch(batchPath, batch_number, emailsBuffer)
            batch_number += 1
    if (len(emailsBuffer) > 0):
        write_batch(batchPath, batch_number, emailsBuffer)
        

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
    byState = defaultdict(list)
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
                        byState[splitext[0]].append(row[4])
                    row_count += 1
        
    print(f"Found {len(emails)} emails")
    print(f"Batching...")
    batch(batchPath, emails);


main()