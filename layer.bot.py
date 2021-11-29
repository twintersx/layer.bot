# pip install speedtest-cli pillow imagehash

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
import os, socket, csv, ctypes, win32clipboard

#pag.displayMousePosition()

# --- Editables --- #
nftName = ''
imageSize = (1400, 1400)
numOfCollections = 2
collection = 'TinMania! large test'
layer0Name = 'Containment Field'
pricing = 'static'
types = ['common', 'unique', 'epic', 'legendary', 'other-worldy', 'god-like'] 
priceDict = {'common': 0.005, 'unique': 0.005, 'epic': 0.005, 'legendary': 0.005, 'other-worldy': 0.01, 'god-like': 0.05}
basePrice = 0.0001 # used only is != static pricing

# --- Globals --- #
nfts = []
traitsData = []
rarityList = []
columnTitles = []
traits = os.listdir('traits')

# --- Setup Functions --- #
def runTimeInfo(pointInTime):
    startTime = time()

    if pointInTime == 'start':
        print(f"Start time: {datetime.now().replace(microsecond = 0)}")

    elif pointInTime == 'nft_creation':
        endTime = round(time() - startTime)
        print(f"This process took: {endTime}s")

    elif pointInTime == 'upload':
        endTime = round((time() - startTime)/60)
        print(f"Upload complete! Total upload time: {endTime} mins")

def getTraitData():
    removeText = ['.png', '-', 'Copy', 'copy', '(', ')']
    for trait in traits:
        combinedTraits = []
        variations = os.listdir(os.path.join('traits', trait))
        for variation in variations:
            variationPath = os.path.join('traits', trait, variation)

            if '.BridgeSort' in variation:
                os.remove(variationPath)
                continue

            for text in removeText:
                variation = variation.replace(text, '')
            variation = ''.join(i for i in variation if not i.isdigit()).strip().title()

            hash = hashImage(variationPath) 

            if not any(hash in l for l in combinedTraits):
                if hash == '8000000000000000':
                    combinedTraits.append([variation, hash, 1])
                else:
                    combinedTraits.append([variation, hash, 0])

        traitsData.append(combinedTraits)

def getListFromFile():
    with open('nfts.csv', mode = 'r') as nftFile:
        reader = csv.reader(nftFile, delimiter = ',')
        next(reader)
        for row in reader:
            nfts.append(row)

def titleRow():
    columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "NFT ID"]
    for trait in traits:
        trait = ''.join(i for i in trait if not i.isdigit()).title().replace('_', '')
        columnTitles = list(chain(columnTitles, [trait, f"{trait} ID", f"{trait} %"]))
    
    columnTitles = list(chain(columnTitles, ["Rarity Score", "Listing Price", "Rarity Type", "Rarity Counts", "Description", "Listed on OpenSea?", "Contract Address", "token_id"]))
    return columnTitles

def desiredNFTCount():
    maxNFTs = 1
    for traits in traitsData:
        if 'Blank' not in traits:
            maxNFTs *= len(traits)

    current = len(os.listdir("nfts"))
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
    return desired, current, i

# --- Layering Functions --- #
def hashImage(filePathName):
    with Image.open(filePathName) as img:
        hash = str(phash(img))
    return hash    

def crcOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def generateRandomStack():
    hashedVariations = []
    imageStack = Image.new('RGBA', imageSize)
    for trait in traits:
        variationDir = os.path.join('traits', trait)
        randomVariation = choice(os.listdir(variationDir))
        variationPath = os.path.join(variationDir, randomVariation)

        hashedVariations.append(hashImage(variationPath))

        traitToLayer = Image.open(variationPath)
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))

    return imageStack, hashedVariations

def checkSavedNFT(filePathName, imageStack, hashedVariations, i):
    size = str(os.path.getsize(filePathName))
    if any(size in s for s in nfts):

        crcValue = crcOnNFT(filePathName)
        if any(crcValue in c for c in nfts):
            
            hash = hashImage(filePathName)
            if any(hash in h for h in nfts):
                os.remove(filePathName)

        else:
            nfts.append(list(chain([size, crcValue, hashImage(filePathName), imageStack], hashedVariations)))
            i += 1
    else:
        nfts.append(list(chain([size, crcOnNFT(filePathName), hashImage(filePathName), imageStack], hashedVariations)))
        i += 1 

    return i  

# --- Write .csv Functions --- # 
def updatenftData(current, rarityList, columnTitles):
    for nftIndex, nftData in enumerate(nfts):
        i = 4
        rarity = 1

        for traits in traitsData:
            for variationList in traits:

                hash = variationList[1]
                if hash in nftData:
                    hashIndex = nftData.index(hash)

                    percentage = variationList[2]
                    if percentage == 0:
                        count = sum(x.count(hash) for x in nfts) + 1
                        variationList[2] = round(count / len(nfts), 3) 

                    if nftIndex + 1 > current: 
                        nftData.remove(nftData[hashIndex]) 
                        nftData.insert(hashIndex, variationList)
                    else:
                        nftData[hashIndex+1] = variationList[2]
        
        for i, data in enumerate(nftData):
            if not isinstance(data, list):
                nftData[i] = [data]
        nftData = [item for sublist in nftData for item in sublist]

        for data in nftData:
            if isinstance(data, float):
                rarity *= data
        rarityScore = round(1 / rarity)
        rarityList.append(rarityScore)
        listingPrice = round(basePrice * rarityScore, 4)

        if nftIndex + 1 > current: 
            nftData.remove(nftData[3]) # delete image object
            nftData.append(rarityScore)
            nftData.append(listingPrice)
            nftData.append('rarity_type_placeholder')
            nftData.append('rarity_count_placeholder')
            nftData.append('description_placeholder')
            nftData.append('no')
            nftData.append('contract_placeholder')
            nftData.append('token_id_placeholder')
            nfts[nftIndex] = list(chain([nftIndex+1, os.path.abspath(f"nfts\\{nftName} #{nftIndex+1}"), f'{nftName} #{nftIndex+1}'], nftData))

        else:
            rarityScoreIndex = columnTitles.index("Rarity Score")
            priceIndex = columnTitles.index("Listing Price")
            nftData[rarityScoreIndex] = rarityScore
            nftData[priceIndex] = listingPrice
            nfts[nftIndex] = nftData

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
                nfts[rIndex][priceIndex] = priceDict[types[t]]  # replaces dynamic listing price with static

            if rareVal < meanVal + t*sDeviation:
                nfts[rIndex][rarityTypeIndex] = types[t]
                break

            elif t == len(types) - 1 and rareVal >= meanVal + t*sDeviation:
                nfts[rIndex][rarityTypeIndex] = types[t]
                break

    for t in types:
        counts = sum(x.count(t) for x in nfts)

        for nftIndex in range (0, len(nfts)):
            if nfts[nftIndex][rarityTypeIndex] == t:
                nfts[nftIndex][rarityTypeIndex + 1] = f"{counts} of {len(nfts)}"

def descriptions(columnTitles):
    for nftIndex, nftData in enumerate(nfts):
        nameIndex = columnTitles.index('Name')
        name = nftData[nameIndex]

        rarityTypeIndex = columnTitles.index('Rarity Type')
        rarity = nftData[rarityTypeIndex].upper()

        rarityCountsIndex = columnTitles.index('Rarity Counts')
        counts = nfts[nftIndex][rarityCountsIndex] 

        """if rarity[0] in 'aeiou':
            word = 'an'
        else: word = 'a'"""

        description = (f"""
                        Chopzy {name} is seen as {rarity} in TinMania.
                        There exists {counts} {rarity} Chopzies in the entire metaverse of TinMania.  
                       """)

        descriptionIndex = columnTitles.index('Description')
        nfts[nftIndex][descriptionIndex] = dedent(description) 

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
    backgroundIndex = titles.index(layer0Name)
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
    #pag.click(300, 300)

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

                nfts[nftIndex][contractIndex] = contractAddress
                nfts[nftIndex][token_idIndex] = token_id
                uploadState = 'yes'
                nfts[nftIndex][listedIndex] = uploadState
                break

    pag.hotkey('ctrl', 'w')            
    # change to press close window and then start over again
    if nftIndex != len(nfts) - 1:
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
    
    shuffle(nfts)

    i = 0
    for nftIndex, nftRow in enumerate(nfts):
        if nftRow[listedIndex] == 'no':
            uploadState = 'no'
            while uploadState == 'no':
                uploadState = listNFT(nftRow, nftIndex, titles)

            with open('nfts.csv', mode = 'w', newline = '') as dataFile:
                writer = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
                writer.writerow(titles)
                writer.writerows(nfts)
                i += 1

    runTimeInfo('upload')  

# --- Setup --- #
getTraitData()
columnTitles = titleRow() 
desiredNFTs, current, i = desiredNFTCount()

# --- Layering --- #
while len(nfts) < desiredNFTs:
    imageStack, hashedVariations = generateRandomStack()
    filePathName = f'nfts\\{nftName} #{i}.PNG'
    imageStack.save(filePathName, 'PNG')
    i = checkSavedNFT(filePathName, imageStack, hashedVariations, i)

# --- Write to .csv --- #
updatenftData(current, rarityList, columnTitles)                
rarityTypes(rarityList, columnTitles)
descriptions(columnTitles)   
with open('nfts.csv', mode = 'r+', newline = '') as dataFile:
    nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    nftCSV.writerow(columnTitles)
    nftCSV.writerows(nfts)

# --- Minting --- #
mintOnOpenSea(columnTitles)