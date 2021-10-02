import os
from socket import socket
from random import choice
from zlib import crc32
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash

startTime = time()
sizes = []
crcList = []
hashes = []
traitsData = []
traits = os.listdir('Traits')

def runTimeInfo(pointInTime):
    if pointInTime == 'start':
        print(f"Bot started on: {datetime.now().replace(microsecond = 0)}")
    elif pointInTime == 'end':
        endTime = round(time() - startTime)
        print(f"Bot finished. Runtime: {endTime}s")

def desiredNFTCounts():
    desiredNFTs = 1
    for trait in traitsData:
        desiredNFTs = desiredNFTs * len(trait)
    print(f"Now creating {desiredNFTs} unique NFT images...")
    return desiredNFTs

def hashNFT(filePathName):
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
            hash = hashNFT(variationPath)
            clonedHashes.append(hash)

        for hash in clonedHashes:
            percentOfVariation = round(100*clonedHashes.count(hash) / len(variations))
            data = [hash, percentOfVariation]

            if data not in variationData:
                variationData.append(data)
    
        traitsData.append(variationData)
    
def pickRandomTraits(): 
    randomTraits = []  
    for trait in traits:
        variationDir = os.path.join('Traits', trait)
        randomVariation = choice(os.listdir(variationDir))
        variationPath = os.path.join(variationDir, randomVariation)

        randomTraits.append(Image.open(variationPath))

    return randomTraits

def saveTraitStackAsNFT(workingTraits, filePathName): 
    imageStack = Image.new('RGBA', (500, 500))
    for img in range(0, len(workingTraits)):
        traitToLayer = workingTraits[img]
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))
    imageStack.save(filePathName, 'PNG')

def cyclicRedundancyCheckOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def currentNFTs():
    return(len(os.listdir('NFTs')))

def addNewSizeCRCandHash(size, crcValue, filePathName):
    sizes.append(size)
    crcList.append(crcValue)

    hash = hashNFT(filePathName)
    hashes.append(hash)

def main():
    runTimeInfo('start')
    
    getTraitData()
    desiredNFTs = desiredNFTCounts()

    i = 1
    while currentNFTs() < desiredNFTs:
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        saveTraitStackAsNFT(pickRandomTraits(), filePathName)

        size = os.path.getsize(filePathName)
        if (size in sizes):
            crcValue = cyclicRedundancyCheckOnNFT(filePathName)
            if (crcValue in crcList):
                hash = hashNFT(filePathName)
                if (hash in hashes):
                    os.remove(filePathName)
            else:
                addNewSizeCRCandHash(size, crcValue, filePathName)
                i += 1
        else:
            addNewSizeCRCandHash(size, cyclicRedundancyCheckOnNFT(filePathName), filePathName)
            i += 1  

    runTimeInfo('end')


