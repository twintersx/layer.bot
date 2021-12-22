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
import os, socket, csv, ctypes, win32clipboard, struct, pickle, shutil

# --- Globals --- #
nfts = []
finals = []
types = ['OEM', 'Luxury', 'Classic', 'Prototype'] 
rarNums = ['5844', '452', '79', '25']

# --- Get nfts[] --- #
with open('nfts - original.csv', mode = 'r') as nftFile:
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
for rowI, nftRow in enumerate(nfts):
    if nftRow[2] not in uploads: 
        continue

    oldName = nftRow[2]
    oldPath = os.path.join(os.getcwd(), "uploads", oldName + '.PNG')

    newName = f"#{newI}"
    description = nftRow[descIndex].replace(oldName, newName)
    nftRow[descIndex] = description

    nftRow[0] = newI
    newPath = os.path.join(os.getcwd(), "finals", newName + '.PNG')
    nftRow[1] = newPath
    shutil.copyfile(oldPath, newPath)
    nftRow[2] = newName
    newI += 1

    finals.append(nftRow)

# --- Recount Rarity --- #
typeIndex = columnTitles.index("Rarity Type")
countIndex = columnTitles.index("Rarity Counts")
for t in types:
    counts = sum(x.count(t) for x in finals)

    for rowI, nftRow in enumerate(finals):
        if nftRow[typeIndex] == t:
            finals[rowI][countIndex] = counts

# --- Add New Rarity Count to Final Descriptions --- #
for row, nftRow in enumerate(finals):
    for i, n in enumerate(rarNums):
        if n in nftRow[descIndex]:
            description = nftRow[descIndex].replace(n, str(finals[row][countIndex]))
            description = description.replace("Chopzy", '')
            description = description.replace(" Chopzies", "'s")
            nftRow[descIndex] = description

with open('nfts - final.csv', mode = 'r+', newline = '') as dataFile:
    nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    nftCSV.writerow(columnTitles)
    nftCSV.writerows(finals)
