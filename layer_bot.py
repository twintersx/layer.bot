# TO DO: If enough images in NFT folder, ask what image you want to start listing nfts on opensea
# DONE: figure out how many of that particular variation is in total collection
# DONE: variation names that do not have a number here: name# are not filtered correctly in gettraitsData()
# DONE: integrate how many NFTs you want for this launch. If desired is greater than ability to make, say you need more variations or traits
# do we generate entire collection at once and select which to upload or generate in sections and upload at once? 
# rounding percentages and price are still an issue
# layer names in masterList should be presentable to the public. Captitalize first letter of each word and remove - and copies and .png
# rarity value should have more decimal points. Also assign after rarity a stamp of rarity: common, unique, rare, legendary, etc
# when creating a small number, some layers will be the only layer in the collection. 

import os, socket, struct, pickle, csv, re
from random import choice
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash
from itertools import chain
from zlib import crc32

# cntrl + k + 1 to hide all functions

startTime = time()
basePrice = 0.01 # move this somewhere else
traitsData = []
nftMasterList = []
traits = os.listdir('Traits')

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
            if not any(data[1] in l for l in combinedTraits):
                combinedTraits.append(data)

        traitsData.append(combinedTraits)

def getServerIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def desiredNFTCount():
    maxNFTs = 1
    for uniqueTrait in traitsData:
        maxNFTs = maxNFTs * len(uniqueTrait)

    while True:
        requested = int(input ("Create how many NFT images?: "))
        current = len(os.listdir("NFTs"))
        ableToMake = maxNFTs - current
        if requested > ableToMake:
            print(f"Limit reached. Reduce to less than {ableToMake}.")
            print(f"Previously created {current} NFTs.")
            print(f"Maximum allowable: {maxNFTs} (based on current layers & traits)")
        newNFTIndex = requested + current
        return newNFTIndex, current

def initializeSocket(sock):
    if getServerIP() == '192.168.1.5':
        socketType = 'server'
        sock.bind(('0.0.0.0', 1200))
        sock.listen(10)
        s, addr = sock.accept()
        print ("Client connected:", addr)
    else:
        socketType = 'client'
        sock.connect(('192.168.1.5', 1200))
        s = None

    return s, socketType

def generateRandomStack():
    unhashedPaths = []
    imageStack = Image.new('RGBA', (500, 500))
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
                filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
                receivedList[3].save(filePathName, 'PNG')
                nftMasterList.append(receivedList)
                i += 1
                break 

    return i

def saveNFTListToFile():
    with open('nftMasterList.csv', mode = 'w', newline = "") as nftFile:
        savedNFTList = csv.writer(nftFile, delimiter = ',')
        savedNFTList.writerows(nftMasterList)

def writeNFTCSV(socketType):
    if socketType == 'server':

        with open('NftCollectionData.csv', mode = 'w', newline = '') as dataFile:
            nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "Image Hash"]
            for i in range (1, len(traits) + 1):
                columnTitles.append(f"Layer {i} Name")
                columnTitles.append(f"Layer {i} Hash")
                columnTitles.append(f"Layer {i} Percentage")
            columnTitles.append("Rarity")
            columnTitles.append("Listing Price (ETH or WETH)")


            for nftIndex, nftDataList in enumerate(nftMasterList):
                nftDataList.remove(nftDataList[3])
                i = 4
                rarity = 1

                for traitList in traitsData:
                    for variationList in traitList:

                        if variationList[1] in nftDataList:
                            hashIndex = nftDataList.index(variationList[1])
                            nftDataList.remove(nftDataList[hashIndex]) 


                            count = sum(x.count(variationList[1]) for x in nftMasterList)
                            if count == 1:
                                pass
                            variationList[2] = count / len(nftMasterList)  

                            nftDataList.insert(hashIndex, variationList)
                

                for i, data in enumerate(nftDataList):
                    if not isinstance(data, list):
                        nftDataList[i] = [data]
                
                nftDataList = [item for sublist in nftDataList for item in sublist]


                for data in nftDataList:
                    if isinstance(data, float) and data != 0.0:
                        rarity *= data
                        
                nftDataList.append(rarity)
                nftDataList.append(basePrice / rarity)
                
            
                nftMasterList[nftIndex] = list(chain([nftIndex+1, os.path.abspath("NFTs"), f'Tin Woodman #{nftIndex+1}'], nftDataList))
            
            nftCSV.writerow(columnTitles)
            nftCSV.writerows(nftMasterList)
    
def getListFromFile():
    with open('nftMasterList.csv', mode = 'r') as nftFile:
        savedNFTReader = csv.reader(nftFile, delimiter = ',')
        for row in savedNFTReader:
            nftMasterList.append(row)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock)
    desiredNFTs, currentNFTs = desiredNFTCount()
    runTimeInfo('start')

    i = 1
    if currentNFTs > 0: 
        getListFromFile()
        i = currentNFTs + 1

    while len(nftMasterList) < desiredNFTs:
        imageStack, hashedVariations = generateRandomStack()
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        imageStack.save(filePathName, 'PNG')

        if socketType == 'client':
            listToSend = createListToSend(filePathName, imageStack, hashedVariations)
            sock.send(listToSend)
            os.remove(filePathName) 

        elif socketType == 'server':
            i = checkSavedNFT(filePathName, imageStack, hashedVariations, i)
            i = checkReceivedNFT(receivePackadge(s), i)

    sock.close()
    saveNFTListToFile()
    writeNFTCSV(socketType)

getTraitData()
main()
runTimeInfo('end')