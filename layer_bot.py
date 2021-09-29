import os, random, imagehash, datetime, zlib
from PIL import Image

sizes = []
crcList = []
hashes = []
traitsData = []
traits = os.listdir('Traits')

def runTimeInfo():
    print(f"Bot started on: {datetime.datetime.now().replace(microsecond = 0, second = 0)}")

def hashNFT(filePathName):
    with Image.open(filePathName) as img:
        hash = str(imagehash.average_hash(img))
    return hash

def getTraitData():
    for tIndex in range(0, len(traits)):
        variationData = []
        clonedHashes = []
        variations = os.listdir(os.path.join('Traits', traits[tIndex]))
        
        for vIndex in range(0, len(variations)):
            variationPath = os.path.join('Traits', traits[tIndex], variations[vIndex])
            clonedHashes.append(hashNFT(variationPath))

        for hash in clonedHashes:
            percentOfVariation = round(100*clonedHashes.count(hash) / len(variations))
            hashData = [hash, percentOfVariation]

            if hashData not in variationData:
                variationData.append(hashData)
        
        traitsData.append(variationData)

def desiredNFTCounts():
    desiredNFTs = 1
    for trait in traitsData:
        desiredNFTs = desiredNFTs * len(trait)
    print(f"Now creating {desiredNFTs} unique NFT images...")
    return desiredNFTs

def pickRandomTraits(): 
    randomTraits = []  
    for t in traits:
        variationDir = os.path.join('Traits', t)
        randomVariation = random.choice(os.listdir(variationDir))
        randomTraits.append(Image.open(os.path.join(variationDir, randomVariation)))
    return randomTraits

def saveTraitStackAsNFT(filePathName):
    workingTraits = pickRandomTraits()
    stackOfLayers = workingTraits[0]  
    for img in range(0, len(workingTraits)-1):
        traitToLayer = workingTraits[img + 1]
        stackOfLayers.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))
    flattenedTraits = stackOfLayers
    flattenedTraits.save(filePathName, 'PNG')

def cyclicRedundancyCheckOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def currentNFTs():
    return(len(os.listdir('NFTs')))

def addNewSizeCRCandHash(filePathName):
    size = os.path.getsize(filePathName)
    sizes.append(size)

    crcValue = cyclicRedundancyCheckOnNFT(filePathName)
    crcList.append(crcValue)

    hash = hashNFT(filePathName)
    hashes.append(hash)

def main():
    desiredNFTs = desiredNFTCounts()

    i = 1
    while currentNFTs() < desiredNFTs:
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        saveTraitStackAsNFT(filePathName)

        size = os.path.getsize(filePathName)
        if (size in sizes):
            crcValue = cyclicRedundancyCheckOnNFT(filePathName)
            if (crcValue in crcList):
                hash = hashNFT(filePathName)
                if (hash in hashes):
                    os.remove(filePathName)
            else:
                addNewSizeCRCandHash(filePathName)
                i += 1
        else:
            addNewSizeCRCandHash(filePathName)
            i += 1  

runTimeInfo()
getTraitData()
main()