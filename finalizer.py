from PIL import Image
from zlib import crc32
from numpy import save
import webbrowser as wb
import pyautogui as pag
from ctypes import windll
from imagehash import phash
import PIL.ImageGrab as pxl
from textwrap import dedent
from itertools import chain
from time import time, sleep
from datetime import datetime
from random import choice, shuffle
from statistics import stdev, mean
import os, socket, csv, ctypes, win32clipboard, struct, pickle

# --- Globals --- #
nfts = []
types = ['OEM', 'Luxury', 'Classic', 'Prototype'] 
rarNums = ['5844', '452', '79', '25']

# --- Get nfts[] --- #
with open('nfts.csv', mode = 'r') as nftFile:
    reader = csv.reader(nftFile, delimiter = ',')
    next(reader)
    for row in reader:
        rowData = []
        for x in row:
            try: 
                if int(x): 
                    item = int(x)
                elif float(x): 
                    item = float(x)
            except: 
                item = x
            rowData.append(item)
        nfts.append(rowData)

traits = os.listdir('traits')
columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "NFT ID"]
for trait in traits:
    trait = ''.join(i for i in trait if not i.isdigit()).title().replace('_', '')
    columnTitles = list(chain(columnTitles, [trait, f"{trait} ID", f"{trait} %"]))
columnTitles = list(chain(columnTitles, ["Rarity Score", "Listing Price", "Rarity Type", "Rarity Counts", "Description", "Listed on OpenSea?", "Contract Address", "token_id"]))

# --- Uploads list --- #
descIndex = columnTitles.index('Description')
uploads = os.listdir("uploads")
uploads = [s.replace(".PNG", "") for s in uploads]

# --- Delete/Keep Appropriate Images --- #
newI = 1
for rowI, nftRow in enumerate(nfts) :
    name = nftRow[2]
    path = os.path.join('nfts', name + '.PNG')

    if name not in uploads:
        nfts.remove(nftRow)
        os.remove(path)

    else: 
        newName = f"#{newI}"
        oldName = nfts[rowI][2]
        description = nftRow[descIndex].replace(oldName, newName)
        nftRow[descIndex] = description

        nfts[rowI][0] = newI
        newPath = os.path.join(os.getcwd(), "nfts", newName + '.PNG')
        nfts[rowI][1] = newPath
        #os.rename(path, newPath)
        nfts[rowI][2] = newName
        newI += 1

# --- Recount Rarity --- #
typeIndex = columnTitles.index("Rarity Type")
countIndex = columnTitles.index("Rarity Counts")
for t in types:
    counts = sum(x.count(t) for x in nfts)

    for rowI, nftRow in enumerate(nfts):
        if nftRow[typeIndex] == t:
            nfts[rowI][countIndex] = counts

# --- Add New Rarity Count to Final Descriptions --- #
for row, nftRow in enumerate(nfts):
    for i, n in enumerate(rarNums):
        if n in nftRow[descIndex]:
            description = nftRow[descIndex].replace(n, str(nfts[row][countIndex]))
            description = description.replace("Chopzy", '')
            description = description.replace("Chopzies", '')
            nftRow[descIndex] = description

with open('nfts.csv', mode = 'r+', newline = '') as dataFile:
    nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    nftCSV.writerow(columnTitles)
    nftCSV.writerows(nfts)
