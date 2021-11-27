# add comments
# add leading zeros to description
# update all opensea info w/ latest from dad
# add all stuff under imports in setup /
# csv hashes and traits are not what corresponds to image when using shuffle, maybe it works without shuffle

# pip install speedtest-cli pillow imagehash

from PIL import Image
from zlib import crc32
import webbrowser as wb
from numpy import save
import pyautogui as pag
from random import choice, shuffle
from ctypes import windll
import PIL.ImageGrab as pxl
from textwrap import dedent
from itertools import chain
from time import time, sleep
from datetime import datetime
from imagehash import average_hash
from statistics import stdev, mean
import os, socket, csv, ctypes, win32clipboard

#pag.displayMousePosition()

nftName = ''
numOfCollections = 2
collection = 'test collection TinMania!'
imageSize = (1400, 1400)
background = 'Containment Field'

pricing = 'static'
types = ['common', 'unique', 'epic', 'legendary', 'other-worldy', 'god-like'] 
priceDict = {'common': 0.005, 'unique': 0.005, 'epic': 0.005, 'legendary': 0.005, 'other-worldy': 0.01, 'god-like': 0.05}
basePrice = 0.0001

traitsData = []
columnTitles = []
startTime = time()
nftMasterList = []
traits = os.listdir('Traits')
rarityList = []
columnTitles = []

# --- Setup Functions --- #
def runTimeInfo(pointInTime):
    if pointInTime == 'start':
        print(f"Start time: {datetime.now().replace(microsecond = 0)}")
        print("Flattening layers...")

    elif pointInTime == 'nft_creation':
        endTime = round(time() - startTime)
        print(f"This process took: {endTime}s")

    elif pointInTime == 'upload':
        endTime = round((time() - startTime)/60)
        print(f"Upload complete! Total upload time: {endTime} mins")

def getTraitData():
    for trait in traits:
        clonedHashes = []
        combinedTraits = []
        variations = os.listdir(os.path.join('Traits', trait))
        
        for variation in variations:
            variationPath = os.path.join('Traits', trait, variation)

            if '.BridgeSort' in variation:
                os.remove(variationPath)
            else:
                hash = hashImage(variationPath)
                clonedHashes.append([variation, hash])

        for data in clonedHashes:
            removeText = ['.png', '-', 'Copy', 'copy', '(', ')']
            for text in removeText:
                data[0] = data[0].replace(text, '')

            data[0] = ''.join(i for i in data[0] if not i.isdigit()).strip().title()

            if data[1] == '0000000000000000':
                data[0] = 'Blank'
                data.append(1)
            else:
                data.append(0)

            if not any(data[1] in l for l in combinedTraits):
                combinedTraits.append(data)

        traitsData.append(combinedTraits)

def getListFromFile():
    with open('NftCollectionData.csv', mode = 'r') as nftFile:
        savedNFTReader = csv.reader(nftFile, delimiter = ',')
        for row in savedNFTReader:
            nftMasterList.append(row)

        try: del nftMasterList[0]
        except: pass

def titleRow():
    columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "NFT ID"]
    for trait in traits:
        trait = ''.join(i for i in trait if not i.isdigit()).title().replace('_', '')
        columnTitles = list(chain(columnTitles, [trait, f"{trait} ID", f"{trait} %"]))
    
    columnTitles = list(chain(columnTitles, ["Rarity Score", "Listing Price", "Rarity Type", "Rarity Counts", "Description", "Listed on OpenSea?", "Contract Address", "token_id"]))

def desiredNFTCount():
    maxNFTs = 1
    for uniqueTrait in traitsData:
        if uniqueTrait[0] != 'Blank':
            maxNFTs *= len(uniqueTrait)

    current = len(os.listdir("NFTs"))
    print(f"Found {current} flattened images. Maximum allowed with current layers: {maxNFTs}")
    
    while True:
        try:
            requested = int(input("How many more would you like to create? "))
            break
        except:
            print("Enter a number...")
    
    ableToMake = maxNFTs - current

    if requested > ableToMake:
        print(f"CANNOT MAKE THIS AMOUNT!")
        print(f"Previously created: {current}")
        print(f"Maximum allowable: {maxNFTs} (based on current layers & traits)")
        print(f"I can only make {ableToMake} more.")
        raise ValueError("Please restart the bot...")

    desired = requested + current

    i = 1
    if current > 0:
        getListFromFile()
        i = current + 1

    runTimeInfo('start')
    return desired, i

# --- Layering Functions --- #
def hashImage(filePathName):
    with Image.open(filePathName) as img:
        hash = str(average_hash(img))
    return hash    

def crcOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def generateRandomStack():
    unhashedPaths = []
    imageStack = Image.new('RGBA', imageSize)
    for trait in traits:
        variationDir = os.path.join('Traits', trait)
        randomVariation = choice(os.listdir(variationDir))
        variationPath = os.path.join(variationDir, randomVariation)

        unhashedPaths.append(hashImage(variationPath))

        traitToLayer = Image.open(variationPath)
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))

    return imageStack, unhashedPaths

def checkSavedNFT(filePathName, imageStack, hashedVariations, i):
    size = os.path.getsize(filePathName)
    if any(size in s for s in nftMasterList):

        crcValue = crcOnNFT(filePathName)
        if any(crcValue in c for c in nftMasterList):
            
            hash = hashImage(filePathName)
            if any(hash in h for h in nftMasterList):
                os.remove(filePathName)

        else:
            nftMasterList.append(list(chain(size, crcValue, hashImage(filePathName), imageStack, hashedVariations)))
            i += 1
    else:
        nftMasterList.append(list(chain([size, crcOnNFT(filePathName), hashImage(filePathName), imageStack], hashedVariations)))
        i += 1 

    return i  

# --- Write .csv Functions --- # 
def updateNFTDataLists(rarityList, columnTitles):
    with open('NftCollectionData.csv', mode = 'r', newline = '') as dataFile:
        reader = list(csv.reader(dataFile))

    for nftIndex, nftDataList in enumerate(nftMasterList):
        nftDataList.remove(nftDataList[3])
        i = 4
        rarity = 1

        for traitList in traitsData:
            for variationList in traitList:

                if variationList[1] in nftDataList:
                    hashIndex = nftDataList.index(variationList[1])
                    nftDataList.remove(nftDataList[hashIndex]) 

                    if variationList[2] == 0:
                        count = sum(x.count(variationList[1]) for x in nftMasterList) + 1
                        variationList[2] = round(count / len(nftMasterList), 3)

                    nftDataList.insert(hashIndex, variationList)
        
        for i, data in enumerate(nftDataList):
            if not isinstance(data, list):
                nftDataList[i] = [data]
        
        nftDataList = [item for sublist in nftDataList for item in sublist]

        for data in nftDataList:
            if isinstance(data, float):
                rarity *= data
        
        rarityScore = 1 / rarity
        rarityList.append(rarityScore)
        nftDataList.append(round(rarityScore))

        nftDataList.append(round(basePrice * rarityScore, 4))

        nftDataList.append('rarity_type_placeholder')
        nftDataList.append('rarity_count_placeholder')
        nftDataList.append('description_placeholder')

        try:
            nftRow = reader[nftIndex + 1]
            listedIndex = columnTitles.index("Listed on OpenSea?")
            if nftRow[listedIndex] == 'yes':
                nftDataList.append('yes')
            else:
                nftDataList.append('no')
        except:
            nftDataList.append('no')

        nftDataList.append('contract_placeholder')
        nftDataList.append('token_id_placeholder')

        nftMasterList[nftIndex] = list(chain([nftIndex+1, os.path.abspath(f"NFTs\\{nftName} #{nftIndex+1}"), f'{nftName} #{nftIndex+1}'], nftDataList))

def rarityTypes(rarityList, columnTitles):
    rarityTypeIndex = columnTitles.index('Rarity Type')
    priceIndex = columnTitles.index('Listing Price')

    sDeviation = round(stdev(rarityList))
    meanVal = round(mean(rarityList))
    """print('stand dev:', sDeviation)
    print('meanVal:', meanVal)
    print('sigma +1', meanVal + 1*sDeviation)
    print('sigma +2', meanVal + 2*sDeviation)
    print('sigma +3', meanVal + 3*sDeviation)
    print('sigma +4', meanVal + 4*sDeviation)"""

    for rIndex, rareVal in enumerate(rarityList):
        for t in range(0, len(types)):
            if pricing == 'static':
                nftMasterList[rIndex][priceIndex] = priceDict[types[t]]

            if rareVal < meanVal + t*sDeviation:
                nftMasterList[rIndex][rarityTypeIndex] = types[t]
                break

            elif t == len(types) - 1 and rareVal >= meanVal + t*sDeviation:
                nftMasterList[rIndex][rarityTypeIndex] = types[t]
                break

    for t in types:
        counts = sum(x.count(t) for x in nftMasterList)

        for nftIndex in range (0, len(nftMasterList)):
            if nftMasterList[nftIndex][rarityTypeIndex] == t:
                nftMasterList[nftIndex][rarityTypeIndex + 1] = f"{counts} of {len(nftMasterList)}"

def descriptions(columnTitles):
    for nftIndex, nftDataList in enumerate(nftMasterList):
        nameIndex = columnTitles.index('Name')
        name = nftDataList[nameIndex]

        rarityTypeIndex = columnTitles.index('Rarity Type')
        rarity = nftDataList[rarityTypeIndex].upper()

        rarityCountsIndex = columnTitles.index('Rarity Counts')
        counts = nftMasterList[nftIndex][rarityCountsIndex] 

        if rarity[0] in 'aeiou':
            word = 'an'
        else: word = 'a'

        description = (f"""
                        Chopzy {name} is seen as {word} {rarity} in TinMania.
                        There exists {counts} {rarity} Chopzies in the entire metaverse of TinMania.  
                       """)

        descriptionIndex = columnTitles.index('Description')
        nftMasterList[nftIndex][descriptionIndex] = dedent(description) 

# --- Mint/Upload Functions --- #
def messageBox():
    message = ("""
                Check that your Metamask wallet is connected.
                Hitting "Ok" will start the minting process...
                You need to be on https://opensea.io/asset/create
                """)
    title = "NFT Creator: \u00A1Atención!"  

    while True:
        try:
            response = ctypes.windll.user32.MessageBoxW(None, dedent(message), title, 0x1000)
            if response == 1:
                break
        except Exception as e: print(e)

def tab(count, delay):
    for _ in range(0, count):
        pag.press('tab')
        sleep(delay)

def click(button, delay):
    if button == 'imageBox':
        pag.click(725, 400)

    elif button == 'sell':
        pag.click(1450, 215)
    
    elif button == 'completeListing':
        pag.click(275, 832)

    elif button == 'sign1':
        pag.click(675, 615)

    elif button == 'sign2':
        pag.click(1825, 550)

    sleep(delay)

def internet():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def listNFT(nftRow, nftIndex, titles):
    path = nftRow[1]
    name = nftRow[2]
    description = nftRow[titles.index('Description')]
    backgroundIndex = titles.index(background)
    rarityScoreIndex = titles.index('Rarity Score')
    price = str(nftRow[titles.index('Listing Price')])
    listedIndex = titles.index("Listed on OpenSea?")
    contractIndex = titles.index("Contract Address")
    token_idIndex = titles.index("token_id")

    # Upload NFT via Image Box
    click('imageBox', 1.25)
    pag.write(path, interval=0.01)
    sleep(0.5)
    pag.press('enter')
    sleep(1.25)
    pag.click(300, 300)

    # Enter name
    tab(2, 0.1)
    pag.write(name, interval=0.005)
    
    # Enter description
    tab(3, 0.1)
    pag.write(description, interval=0.005)

    # Type collection name
    tab(1, 0.1)
    pag.write(collection, interval=0.005)
    sleep(1)
    tab(1, 0.1)
    pag.press('enter')
    sleep(0.5)
    tab(2 + numOfCollections, 0) 

    # Enter Trait info
    pag.press('enter')
    sleep(0.5)
    loopCount = 1   
    for traitIndex in range(backgroundIndex, rarityScoreIndex-2, 3):
        if nftRow[traitIndex] == 'Blank':
            continue
        pag.write(titles[traitIndex])
        tab(1, 0)
        pag.write(nftRow[traitIndex])
        tab(1, 0)
        if rarityScoreIndex-3 == traitIndex:
            break
        pag.press('enter')
        pag.hotkey('shift', 'tab')
        pag.hotkey('shift', 'tab')
        loopCount += 1  #always one more than traits listed
    tab(3, 0)
    pag.press('enter')
    sleep(0.5)

    # Select Polygon network
    tab(loopCount + 6, 0.25)
    pag.press('enter')
    sleep(0.25)

    # Complete listing (finish minting)
    tab(3, 0.25)
    pag.press('enter')

    # Wait until minting is complete and return to collection page
    sellColors = pxl.grab().load()[1440, 220]
    while sellColors[0] > 33:
        pag.press('esc')
        sellColors = pxl.grab().load()[1440, 220]
        sleep(0.5)

    # Press Sell NFT
    click('sell', 1)

    polyColors = pxl.grab().load()[215, 436]
    while polyColors[0] > 200:
        polyColors = pxl.grab().load()[215, 436]
        sleep(0.25)

    # Enter listing price
    pag.write(price, interval=0.01)

    compListColors = pxl.grab().load()[205, 825]
    while compListColors[0] > 33:
        compListColors = pxl.grab().load()[205, 825]
        sleep(0.25)

    # Complete Listing on sell page
    click('completeListing', 1)

    sign1Colors = pxl.grab().load()[660, 600]
    while sign1Colors[0] > 33:
        sign1Colors = pxl.grab().load()[660, 600]
        sleep(0.25)

    # 1st sign on OpenSea
    click('sign1', 0.25)

    sign2Colors = pxl.grab().load()[1780, 550]
    while sign2Colors[0] > 33:
        sign2Colors = pxl.grab().load()[1780, 550]
        sleep(0.25)

    # 2nd sign on Metamask
    click('sign2', 2)

    uploadState = 'no'
    if internet():
        pag.hotkey('ctrl', 'l')
        sleep(0.1)
        pag.hotkey('ctrl', 'c')

        win32clipboard.OpenClipboard()
        url = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        paths = url.split('/')
        for i, path in enumerate(paths):
            if '0x' in path:
                contractAddress = path
                token_id = paths[i+1]

                nftMasterList[nftIndex][contractIndex] = contractAddress
                nftMasterList[nftIndex][token_idIndex] = token_id
                uploadState = 'yes'
                nftMasterList[nftIndex][listedIndex] = uploadState
                break

    pag.hotkey('ctrl', 'w')            
    # change to press close window and then start over again
    if nftIndex != len(nftMasterList) - 1:
        wb.open('https://opensea.io/asset/create', new = 2)
        sleep(2.5)

    return uploadState

def mintOnOpenSea(columnTitles):
    listedIndex = columnTitles.index("Listed on OpenSea?")
    titles = titleRow()
    wb.open('https://opensea.io/asset/create', new=2)
    sleep(2)
    pag.press('f5')
    messageBox()
    sleep(0.75)
    
    #shuffle(nftMasterList)

    i = 0
    for nftIndex, nftRow in enumerate(nftMasterList):
        if nftRow[listedIndex] == 'no':
            uploadState = 'no'
            while uploadState == 'no':
                uploadState = listNFT(nftRow, nftIndex, titles)

            with open('NftCollectionData.csv', mode = 'w', newline = '') as dataFile:
                writer = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
                writer.writerow(titles)
                writer.writerows(nftMasterList)
                i += 1

    runTimeInfo('upload')  

# --- Setup --- #
titleRow()  #put this somewhere else
getTraitData()
desiredNFTs, i = desiredNFTCount()

# --- Layering --- #
while len(nftMasterList) < desiredNFTs:
    imageStack, hashedVariations = generateRandomStack()
    filePathName = f'NFTs\\{nftName} #{i}.PNG'
    imageStack.save(filePathName, 'PNG')
    i = checkSavedNFT(filePathName, imageStack, hashedVariations, i)

# --- Write to .csv --- #
with open('NftCollectionData.csv', mode = 'r+', newline = '') as dataFile:
    nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    updateNFTDataLists(rarityList, columnTitles)                
    if len(nftMasterList) > 1:
        rarityTypes(rarityList, columnTitles)
        descriptions(columnTitles)           
    nftCSV.writerow(columnTitles)
    nftCSV.writerows(nftMasterList)

# --- Minting --- #
mintOnOpenSea(columnTitles)