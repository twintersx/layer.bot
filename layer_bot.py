import os, socket, struct
from io import BytesIO
from random import choice
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash
from itertools import chain
from zlib import crc32
import pickle

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
        variationData = []
        clonedHashes = []
        variations = os.listdir(os.path.join('Traits', traits[tIndex]))
        
        for vIndex in range(0, len(variations)):
            variationPath = os.path.join('Traits', traits[tIndex], variations[vIndex])
            hash = hashImage(variationPath)
            clonedHashes.append(hash)

        for hash in clonedHashes:
            percentOfVariation = round(100*clonedHashes.count(hash) / len(variations))
            data = [hash, percentOfVariation]

            if data not in variationData:
                variationData.append(data)
    
        traitsData.append(variationData)

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

def cyclicRedundancyCheckOnNFT(filePathName):
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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock)
    desiredNFTs = desiredNFTCounts()

    i = 1
    while len(nftList) < desiredNFTs:
        imageStack, hashedVariations = generateRandomStack()
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        imageStack.save(filePathName, 'PNG')

        size = os.path.getsize(filePathName)
        if any(size in s for s in nftList):

            crcValue = cyclicRedundancyCheckOnNFT(filePathName)
            if any(crcValue in c for c in nftList):
                
                hash = hashImage(filePathName)
                if any(hash in h for h in nftList):
                    os.remove(filePathName)

                    if socketType == 'client':
                        for listToSend in nftList:
                            pickledList = pickle.dumps(listToSend)
                            packedData = struct.pack('>I', len(pickledList)) + pickledList
                            sock.send(packedData)

            else:
                addToNFTList = []
                addToNFTList.append(size)
                addToNFTList.append(crcValue)
                addToNFTList.append(hashImage(filePathName))
                addToNFTList.append(imageStack)
                addToNFTList = list(chain(addToNFTList, hashedVariations))
                nftList.append(addToNFTList)
                i += 1
        else:
            addToNFTList = []
            addToNFTList.append(size)
            addToNFTList.append(cyclicRedundancyCheckOnNFT(filePathName))
            addToNFTList.append(hashImage(filePathName))
            addToNFTList.append(imageStack)
            addToNFTList = list(chain(addToNFTList, hashedVariations))
            nftList.append(addToNFTList)
            i += 1


        if socketType == 'server':

            pickledPackadge = receivePackadge(s)
            if pickledPackadge is not None:
                receivedList = pickle.loads(pickledPackadge)

                for data in receivedList:
                    if isinstance(data, Image.Image):
                        break

                    if not any(data in l for l in nftList):
                        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
                        receivedList[3].save(filePathName, 'PNG')
                        nftList.append(receivedList)
                        pickledPackadge = None
                        i += 1
                        break
                


    sock.close()
    # !!!THIS IS FOR DATA AND BOT LISTING INFO!!!
    # when while loop has completed, hash everything to look for any duplicates that may have made it through
    # replace each image (nftList[imageIndex][0]) with the hash of that image.
    # iterate over hashes in each imageIndex, if hash exists in getTraitData, append the percentage value after it. Multiply all percentages together as you iterate to get rarity percentage. 
    # then list(chain(imageIndex, filepath, name of nft, hash of nft, newly hashed list with percentage values, rarity percentage, base cost of NFT divided by rarity of NFT (this is the final cost of NFT, the smaller the percentage the higher the price)))
    # create column names and add to excel spreadsheet
    # use this large list of data to fill in an excel spreadsheet for reference but use the list(chain) to actually list nfts on opensea


runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')