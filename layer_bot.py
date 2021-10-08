# TO DO: If enough images in NFT folder, ask what image you want to start listing nfts on opensea
# figure out how many of that particular variation is in total collection

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
basePrice = 0.01
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

            match = re.match(r"([a-z]+)([0-9]+)", f'{variation}', re.I) 
            if match:
                nameNumSplit = match.groups()
                variationName = nameNumSplit[0]
            else:
                variationName = variation.split('.')[0]

            clonedHashes.append([variationName, hash])

        for data in clonedHashes:
            #percentOfVariation = round(clonedHashes.count(data) / len(variations), 3)
            data = list(chain(data, [0])) 

            if data not in combinedTraits:
                combinedTraits.append(data)

        traitsData.append(combinedTraits)

def getServerIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def desiredNFTCounts():
    desiredNFTs = 1
    for uniqueTrait in traitsData:
        desiredNFTs = desiredNFTs * len(uniqueTrait)
    print(f"Now creating {desiredNFTs} unique NFT images...")
    return desiredNFTs

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
                columnTitles.append(f"Variation {i} Name")
                columnTitles.append(f"Variation {i} Hash")
                columnTitles.append(f"Variation {i} Percentage")
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
                            variationList[2] = count / len(nftMasterList)  

                            nftDataList.insert(hashIndex, variationList)
                

                for i, data in enumerate(nftDataList):
                    if not isinstance(data, list):
                        nftDataList[i] = [data]
                
                nftDataList = [item for sublist in nftDataList for item in sublist]


                for data in nftDataList:
                    if isinstance(data, float):
                        rarity *= data
                        data = round(100*data, 2)
                        

                nftDataList.append(round(rarity, 2))
                nftDataList.append(round(basePrice / rarity, 3))
                
            
                nftMasterList[nftIndex] = list(chain([nftIndex+1, os.path.abspath("NFTs"), f'Tin Woodman #{nftIndex+1}'], nftDataList))
            
            nftCSV.writerow(columnTitles)
            nftCSV.writerows(nftMasterList)
    
def getListFromFile():
    with open('nftMasterList.csv', mode = 'r') as nftFile:
        savedNFTReader = csv.reader(nftFile, delimiter = ',')
        for row in savedNFTReader:
            nftMasterList.append(row)

def main():
    """sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock)"""
    desiredNFTs = desiredNFTCounts()

    socketType = 'server'

    if len(os.listdir("NFTs")) == desiredNFTs:
        getListFromFile()

    i = 1
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
            #i = checkReceivedNFT(receivePackadge(s), i)

    #sock.close()
    saveNFTListToFile()
    writeNFTCSV(socketType)

runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')