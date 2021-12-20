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

nfts = []

def getListFromFile():
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

getListFromFile()

uploads = os.listdir("uploads")
for nftRow in nfts:
    name = nftRow[2]
    if name not in uploads:
        nfts.remove(nftRow)
        path = os.path.join('nfts', name)
        os.remove(path)