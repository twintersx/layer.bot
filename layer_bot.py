# pip install speedtest-cli pillow imagehash tqdm

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
import os, socket, csv, ctypes, win32clipboard, struct, pickle, tqdm

# --- Editables --- #
nftName = ''
imageSize = (1400, 1400)
descriptionInsert = 'Cancer Stick'
pricing = 'static'
types = ['OEM', 'Luxury', 'Classic', 'Prototype'] 
priceDict = {'OEM': 0.005, 'Luxury': 0.01, 'Classic': 0.025, 'Prototype': 0.05}
basePrice = 0.0001 # used only if != static pricing

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
    print("Collecting Trait Data...")
    removeText = ['.jpg', '.png', '-', 'Copy', 'copy', '(', ')']
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
                    variation = 'Blank'
                    combinedTraits.append([variation, hash, 1])
                else:
                    combinedTraits.append([variation, hash, 0])

        traitsData.append(combinedTraits)

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

def titleRow():
    columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "NFT ID"]
    for trait in traits:
        trait = ''.join(i for i in trait if not i.isdigit()).title().replace('_', '')
        columnTitles = list(chain(columnTitles, [trait, f"{trait} ID", f"{trait} %"]))
    
    columnTitles = list(chain(columnTitles, ["Rarity Score", "Listing Price", "Rarity Type", "Rarity Counts", "Description", "Listed on OpenSea?", "Contract Address", "token_id"]))
    return columnTitles

def desiredNFTCount(socketType):
    current = len(os.listdir("nfts"))
    
    maxNFTs = 1
    for traits in traitsData:
        if 'Blank' not in traits:
            maxNFTs *= len(traits)

    print(f"Found {current} flattened images. Maximum allowed with current layers: {maxNFTs}")

    i = 1
    desired = maxNFTs
    if socketType == 'server':
        if current > 0:
            getListFromFile()
            i = current + 1

        requested = int(input("How many more would you like to create? "))
        desired = requested + current

    return desired, current, i

def getIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def initializeSocket(sock, serverIP):
    if getIP() == serverIP:
        socketType = 'server'
        sock.bind(('0.0.0.0', 1200))
        sock.listen(10)
        print ("Waiting for Client connection...")
        s, addr = sock.accept()
        print ("Client connected:", addr)
    else:
        socketType = 'client'
        sock.connect((serverIP, 1200))
        s = None

    return s, socketType

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
        imageStack = Image.alpha_composite(imageStack, traitToLayer.convert('RGBA'))   #paste

    whiteImage = Image.open('white.png')
    whiteImage = whiteImage.resize(imageSize)
    finalImage = Image.alpha_composite(whiteImage, imageStack)

    return finalImage, hashedVariations

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

def createListToSend(filePathName, imageStack, hashedVariations):
    listToSend = []
    listToSend.append(os.path.getsize(filePathName))
    listToSend.append(crcOnNFT(filePathName))
    listToSend.append(hashImage(filePathName))
    listToSend.append(imageStack)

    listToSend = list(chain(listToSend, hashedVariations))
    pickledList = pickle.dumps(listToSend)
    packedData = struct.pack('>I', len(pickledList)) + pickledList

    return packedData

def checkReceivedNFT(pickledPackadge, i):
    if pickledPackadge is not None:
        receivedList = pickle.loads(pickledPackadge)

        for data in receivedList:
            if isinstance(data, Image.Image):
                break

            if not any(data in l for l in nfts):
                filePathName = f'NFTs\\{nftName} #{i}.PNG'
                receivedList[3].save(filePathName.strip(), 'PNG')
                nfts.append(receivedList)
                i += 1
                break 
    return i

def receivePackadge(s):
    def recv_msg(s):
        raw_msglen = recvall(s, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall(s, msglen)

    def recvall(s, n):
        data = bytearray()
        while len(data) < n:
            packet = s.recv(n - len(data))  #stuck receiving
            if not packet:
                return None
            data.extend(packet)
        return data

    return recv_msg(s)

# --- Write .csv Functions --- # 
def updateNftData(current, rarityList, columnTitles):
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
                        variationList[2] = round(count / len(nfts), 4) 

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
        rarityScore = (1 / rarity)
        rarityList.append(rarityScore)
        listingPrice = round(basePrice * rarityScore, 4)

        if nftIndex + 1 > current: 
            nftData.remove(nftData[3]) # delete image object
            nftData.append(rarityScore)
            nftData.append(listingPrice)
            nftData.append('') #rarity_type_placeholder
            nftData.append('') #rarity_count_placeholder
            nftData.append('') #description_placeholder
            nftData.append('no')
            nftData.append('') #contract_placeholder
            nftData.append('') #token_id_placeholder
            nfts[nftIndex] = list(chain([nftIndex+1, os.path.abspath(f"nfts\\{nftName}#{nftIndex+1}"), f'{nftName}#{nftIndex+1}'], nftData))

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

    for rIndex, rareVal in enumerate(rarityList):
        for t in range(0, len(types)):

            if pricing == 'static':
                nfts[rIndex][priceIndex] = priceDict[types[t]]  # replaces dynamic listing price with static

            if t == len(types) - 1 and rareVal >= meanVal + t*sDeviation:
                rareVal /= 5.5   # increase value to increase the amount of rarity type nearest top tier rarity types
                if rareVal < meanVal + t*sDeviation:
                    nfts[rIndex][rarityTypeIndex] = types[t-1]
                    break
                nfts[rIndex][rarityTypeIndex] = types[t]
                break

            elif rareVal < meanVal + t*sDeviation:
                if t == 0:
                    rareVal *= 4   # increase value to reduce the amount of common (OEM) rarity types
                    if rareVal >= meanVal + t*sDeviation and t == 0:
                        nfts[rIndex][rarityTypeIndex] = types[t+1]
                        break

                nfts[rIndex][rarityTypeIndex] = types[t]
                break

    for t in types:
        counts = sum(x.count(t) for x in nfts)

        for nftIndex in range (0, len(nfts)):
            if nfts[nftIndex][rarityTypeIndex] == t:
                nfts[nftIndex][rarityTypeIndex + 1] = f"{counts}"

def descriptions(columnTitles):
    for nftIndex, nftData in enumerate(nfts):
        nameIndex = columnTitles.index('Name')
        name = nftData[nameIndex]

        rarityTypeIndex = columnTitles.index('Rarity Type')
        rarity = nftData[rarityTypeIndex].upper()

        rarityCountsIndex = columnTitles.index('Rarity Counts')
        counts = nfts[nftIndex][rarityCountsIndex] 

        insert = ''
        if descriptionInsert in nftData:
            insert = "100% of TinMania! proceeds from the 'Cancer Stick' trait are donated to the [GO2 Foundation](https://go2foundation.org/get-involved/donate-cryptocurrency/) for Lung Cancer."

        description = (f"""                    Chopzy{name} is seen as {rarity} in TinMania.
                    There exists only {counts} {rarity} Chopzies in the entire metaverse of TinMania.  
                    {insert}""")

        descriptionIndex = columnTitles.index('Description')
        nfts[nftIndex][descriptionIndex] = dedent(description)  

# --- Setup --- #
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIP = '192.168.1.5'
s, socketType = initializeSocket(sock, serverIP)

columnTitles = titleRow() 
getTraitData()
desiredNFTs, current, i = desiredNFTCount(socketType)

# --- Layering --- #
runTimeInfo('start')
while len(nfts) < desiredNFTs:
    imageStack, hashedVariations = generateRandomStack()
    filePathName = f'nfts\\{nftName} #{i}.PNG'
    imageStack.save(filePathName.strip(), 'PNG')

    if socketType == 'client':
        listToSend = createListToSend(filePathName, imageStack, hashedVariations)
        os.remove(filePathName)
        try: sock.send(listToSend)
        except: 
            print("Disconnected from Server.")
            break

    if socketType == 'server':
        i = checkSavedNFT(filePathName, imageStack, hashedVariations, i)
        if len(nfts) < desiredNFTs:
            i = checkReceivedNFT(receivePackadge(s), i)
sock.close()

# --- Write to .csv --- #
if socketType == 'server':
    updateNftData(current, rarityList, columnTitles)                
    rarityTypes(rarityList, columnTitles)
    descriptions(columnTitles)   
    with open('nfts.csv', mode = 'r+', newline = '') as dataFile:
        nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
        nftCSV.writerow(columnTitles)
        nftCSV.writerows(nfts)

# --- Minting --- #
# now in mint_bot.py !