import os, socket, struct, pickle, csv
from random import choice
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash
from itertools import chain
from zlib import crc32

startTime = time()
traitsData = []
nftList = []
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
    for tIndex in range(0, len(traits)):
        clonedHashes = []
        variations = os.listdir(os.path.join('Traits', traits[tIndex]))
        
        for vIndex in range(0, len(variations)):
            variationPath = os.path.join('Traits', traits[tIndex], variations[vIndex])
            hash = hashImage(variationPath)
            clonedHashes.append(hash)

        for hash in clonedHashes:
            percentOfVariation = clonedHashes.count(hash) / len(variations)
            data = [hash, percentOfVariation]

            if data not in traitsData:
                traitsData.append(data)

def getServerIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def desiredNFTCounts():
    desiredNFTs = 1
    for trait in traitsData:
        desiredNFTs = desiredNFTs * len(trait)
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

    listToSend = list(chain(listToSend, [hashedVariations]))
    pickledList = pickle.dumps(listToSend)
    packedData = struct.pack('>I', len(pickledList)) + pickledList

    return packedData

def addNFTData(size, crcValue, filePathName, imageStack, hashedVariations):
    addToNFTList = []
    addToNFTList.append(size)
    addToNFTList.append(crcValue)
    addToNFTList.append(hashImage(filePathName))
    addToNFTList.append(imageStack)
    addToNFTList = list(chain(addToNFTList, [hashedVariations]))
    nftList.append(addToNFTList)

def checkSavedNFT(filePathName, imageStack, hashedVariations, i):
    size = os.path.getsize(filePathName)
    if any(size in s for s in nftList):

        crcValue = crcOnNFT(filePathName)
        if any(crcValue in c for c in nftList):
            
            hash = hashImage(filePathName)
            if any(hash in h for h in nftList):
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

            if not any(data in l for l in nftList):
                filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
                receivedList[3].save(filePathName, 'PNG')
                nftList.append(receivedList)
                i += 1
                break 

    return i

def writeNFTCSV():
    basePrice = 0.01
    with open('NftCollectionData.csv', mode = 'w') as dataFile:
        nftCSV = csv.writer(dataFile, delimiter = ',')
        columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "Image Hash", "PIL Image Object"]
        for i in len(traits):
            columnTitles.append(f"Variation {i} Hash")
        columnTitles.append("Rarity")
        columnTitles.append("Listing Price (ETH or WETH)")
        nftCSV.writerow(columnTitles)

        for i, nftData in enumerate(nftList):
            for variation in nftData[4]:
                    rarity = 1
                    for data in traitsData:
                        if variation == data[0]:
                            rarity = rarity * data[1]

                    nftData.append(rarity)
                    nftData.append(basePrice / rarity)
                    nftList[i] = list(chain([i, os.path.abspath("NFTs"), f'NFTs\\Tin Woodman #{i}.PNG'], nftData))
                    nftCSV.writerow(nftList[i])
    
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock)
    desiredNFTs = desiredNFTCounts()

    i = 1
    while len(nftList) < desiredNFTs:
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
    writeNFTCSV()

runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')