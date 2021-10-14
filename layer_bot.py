# TO DO: 
# create a dictionary so that you never get indexing confused.... 

import os, socket, struct, pickle, csv
import pyautogui as pag
pag.PAUSE = 3
import subprocess as sp
from random import choice
from datetime import datetime
from time import time, sleep
from PIL import Image
from imagehash import average_hash
from itertools import chain
from zlib import crc32
from statistics import stdev, mean
from textwrap import dedent
from winsound import PlaySound, SND_ALIAS

startTime = time()
basePrice = 0.001
nftName = "Lips McGee"
traitsData = []
nftMasterList = []
traits = os.listdir('Traits')

chromePath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

def runTimeInfo(pointInTime):
    if pointInTime == 'start':
        print(f"Bot started on: {datetime.now().replace(microsecond = 0)}")

    elif pointInTime == 'end':
        endTime = round(time() - startTime)
        print(f"Bot finished. Runtime: {endTime}s")

def hashImage(filePathName):
    with Image.open(filePathName) as img:
        hash = str(average_hash(img))
    return hash    

def getTraitData():
    for trait in traits:
        clonedHashes = []
        combinedTraits = []
        variations = os.listdir(os.path.join('Traits', trait))
        
        for variation in variations:
            variationPath = os.path.join('Traits', trait, variation)
            hash = hashImage(variationPath)
            clonedHashes.append([variation, hash])

        for data in clonedHashes:
            data.append(0)
            data[0] = data[0].replace('.png', '').replace('-', '').replace('Copy', '').replace('(', '').replace(')', '')
            data[0] = ''.join(i for i in data[0] if not i.isdigit()).title()
            if not any(data[1] in l for l in combinedTraits):
                combinedTraits.append(data)

        traitsData.append(combinedTraits)

def getServerIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def desiredNFTCount(socketType):
    maxNFTs = 1
    for uniqueTrait in traitsData:
        maxNFTs *= len(uniqueTrait)

    if socketType == 'client':
        return maxNFTs, 0

    current = len(os.listdir("NFTs"))
    print(f"Found {current} NFTs. Maximum allowed with current layers: {maxNFTs}")
    
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

    i = 1
    if current > 0: 
        getListFromFile()
        i = current + 1

    desired = requested + current
    return desired, i

def initializeSocket(sock):
    print(u"\u00A1" + "Bienvenidos!")

    if getServerIP() == '192.168.1.5':
        socketType = 'server'
        sock.bind(('0.0.0.0', 1200))
        sock.listen(10)
        print ("Waiting for Client connection...")
        s, addr = sock.accept()
        print ("Client connected:", addr)
    else:
        socketType = 'client'
        sock.connect(('192.168.1.5', 1200))
        s = None

    return s, socketType

def generateRandomStack():
    unhashedPaths = []
    size = (500, 500)
    imageStack = Image.new('RGBA', size)
    for trait in traits:
        variationDir = os.path.join('Traits', trait)
        randomVariation = choice(os.listdir(variationDir))
        variationPath = os.path.join(variationDir, randomVariation)

        unhashedPaths.append(hashImage(variationPath))

        traitToLayer = Image.open(variationPath)
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))

    return imageStack, unhashedPaths

def crcOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

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

def addNFTData(size, crcValue, filePathName, imageStack, hashedVariations):
    addToNFTList = []
    addToNFTList.append(size)
    addToNFTList.append(crcValue)
    addToNFTList.append(hashImage(filePathName))
    addToNFTList.append(imageStack)
    addToNFTList = list(chain(addToNFTList, hashedVariations))
    nftMasterList.append(addToNFTList)

def checkSavedNFT(filePathName, imageStack, hashedVariations, i):
    size = os.path.getsize(filePathName)
    if any(size in s for s in nftMasterList):

        crcValue = crcOnNFT(filePathName)
        if any(crcValue in c for c in nftMasterList):
            
            hash = hashImage(filePathName)
            if any(hash in h for h in nftMasterList):
                os.remove(filePathName)

        else:
            addNFTData(size, crcValue, filePathName, imageStack, hashedVariations)
            i += 1
    else:
        addNFTData(size, crcOnNFT(filePathName), filePathName, imageStack, hashedVariations)
        i += 1 

    return i

def checkReceivedNFT(pickledPackadge, i):
    if pickledPackadge is not None:
        receivedList = pickle.loads(pickledPackadge)

        for data in receivedList:
            if isinstance(data, Image.Image):
                break

            if not any(data in l for l in nftMasterList):
                filePathName = f'NFTs\\{nftName} #{i}.PNG'
                receivedList[3].save(filePathName, 'PNG')
                nftMasterList.append(receivedList)
                i += 1
                break 
    return i

def saveNFTListToFile():
    with open('nftMasterList.csv', mode = 'w', newline = "") as nftFile:
        savedNFTList = csv.writer(nftFile, delimiter = ',')
        savedNFTList.writerows(nftMasterList)

def titleRow():
    columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "NFT ID"]
    for trait in traits:
        trait = ''.join(i for i in trait if not i.isdigit()).title().replace('_', '')
        columnTitles.append(trait)
        columnTitles.append(f"{trait} ID")
        columnTitles.append(f"{trait} %")
    columnTitles.append("Rarity Score")
    columnTitles.append("Listing Price")
    columnTitles.append("Rarity Type")
    columnTitles.append("Rarity Counts")
    columnTitles.append("Description")
    return columnTitles

def updateNFTDataLists(rarityList):
    for nftIndex, nftDataList in enumerate(nftMasterList):
        nftDataList.remove(nftDataList[3])
        i = 4
        rarity = 1

        for traitList in traitsData:
            for variationList in traitList:

                if variationList[1] in nftDataList:
                    hashIndex = nftDataList.index(variationList[1])
                    nftDataList.remove(nftDataList[hashIndex]) 

                    count = sum(x.count(variationList[1]) for x in nftMasterList) + 1
                    variationList[2] = round(count / len(nftMasterList), 2) 

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
        nftDataList.append(round(basePrice * rarityScore, 2))
        nftDataList.append('rarity_type_placeholder')
        nftDataList.append('rarity_count_placeholder')
        nftDataList.append('description_placeholder')

        nftMasterList[nftIndex] = list(chain([nftIndex+1, os.path.abspath(f"NFTs\\{nftName} #{nftIndex+1}"), f'{nftName} #{nftIndex+1}'], nftDataList))

def rarityTypes(rarityList, columnTitles):
    types = ['common', 'unique', 'epic', 'legendary', 'GOD']
    rarityTypeIndex = columnTitles.index('Rarity Type')

    sDeviation = round(stdev(rarityList))
    meanVal = round(mean(rarityList))
    """print('stand dev:', sDeviation)
    print('meanVal:', meanVal)
    print('sigma +1', meanVal + 1*sDeviation)
    print('sigma +2', meanVal + 2*sDeviation)
    print('sigma +3', meanVal + 3*sDeviation)
    print('sigma +4', meanVal + 4*sDeviation)"""

    for rIndex, rareVal in enumerate(rarityList):
        for t in range(1, len(types)):
            if rareVal < meanVal + t*sDeviation:
                nftMasterList[rIndex][rarityTypeIndex] = types[t - 1]
                break
            elif t == len(types) and rareVal >= meanVal + t*sDeviation:
                nftMasterList[rIndex][rarityTypeIndex] = types[len(types) - 1]
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
                         {name} is {word} **{rarity}** WOZ Tin Man.
                         _There exists only {counts} **{rarity}** Tin Men in the World of Oz._  
                       """)

        descriptionIndex = columnTitles.index('Description')
        nftMasterList[nftIndex][descriptionIndex] = dedent(description)

def writeNFTCSV(socketType):
    if socketType == 'server':
        rarityList = []
        with open('NftCollectionData.csv', mode = 'w', newline = '') as dataFile:
            nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            columnTitles = titleRow()
            updateNFTDataLists(rarityList)
            if len(nftMasterList) > 1:
                rarityTypes(rarityList, columnTitles)
                descriptions(columnTitles)
                            
            nftCSV.writerow(columnTitles)
            nftCSV.writerows(nftMasterList)

        PlaySound("SystemAsterisk", SND_ALIAS)
        print(f"{len(nftMasterList)} NFTs were successfully created... \u00A1Felicidades! ")
        print("****************************************************")
    
def getListFromFile():
    with open('nftMasterList.csv', mode = 'r') as nftFile:
        savedNFTReader = csv.reader(nftFile, delimiter = ',')
        for row in savedNFTReader:
            nftMasterList.append(row)

def tab(count):
    for i in range(1, count):
        pag.press('tab')

def mintOnOpenSea():
    try: sp.check_output("Taskkill /T /F /IM Chrome.exe", stderr=sp.DEVNULL)
    except: pass

    print("Now visiting: https://opensea.io/asset/create")
    sleep(1)
    sp.Popen([chromePath, "https://opensea.io/asset/create"])

    while True:
        try:
            print("Confirm you have signed your MetaMask wallet, before continuing...")
            response = input("Enter 'mint' to mint your collection on OpenSea: ")
            chrome = pag.getWindowsWithTitle('chrome')[0]
            if response == 'mint':
                chrome.maximize()
                break
        except Exception as e: print(e)

    pag.press('f11')
    for nftDataList in nftMasterList:
        pag.click(725, 315) #image box
        pag.write(nftDataList[1])
        pag.press('enter')
        tab(3)

        pag.write(f'{nftDataList[2]}')
        tab(2)

        titles = titleRow()
        descriptionIndex = titles.index('Description')
        pag.write(f'{nftDataList[descriptionIndex]}')

        collectionIndex = 0
        tab(2 + collectionIndex)
        pag.press('enter')
        collections = 2
        tab(2 + collections)

        pag.press('enter')
        
        backgroundIndex = titles.index('Background')
        rarityScoreIndex = titles.index('Rarity Score')
        loopCount = 1
        for traitIndex in range(backgroundIndex, rarityScoreIndex-2, 2):
            pag.write(titles[traitIndex])
            tab(1)
            pag.write(nftDataList[traitIndex])
            tab(1)
            pag.press('enter')
            loopCount += 1
        
        tab(loopCount)
        tab(6)
        pag.press('enter')
        tab(5)
        pag.press('enter')
        break

def main():
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s, socketType = initializeSocket(sock)
    socketType = 'server'
    desiredNFTs, i = desiredNFTCount(socketType)
    runTimeInfo('start')

    while len(nftMasterList) < desiredNFTs:
        imageStack, hashedVariations = generateRandomStack()
        filePathName = f'NFTs\\{nftName} #{i}.PNG'
        imageStack.save(filePathName, 'PNG')

        if socketType == 'client':
            listToSend = createListToSend(filePathName, imageStack, hashedVariations)
            """try: sock.send(listToSend)
            except: 
                print("Disconnected from Server.")
                exit()"""
            os.remove(filePathName)

        elif socketType == 'server':
            i = checkSavedNFT(filePathName, imageStack, hashedVariations, i)
            """if len(nftMasterList) < desiredNFTs:
                i = checkReceivedNFT(receivePackadge(s), i)"""

    #sock.close()
    saveNFTListToFile()
    writeNFTCSV(socketType)

    mintOnOpenSea()

#pag.displayMousePosition()
getTraitData()
main()
runTimeInfo('end')