import os, random, imagehash, datetime, zlib, time, itertools
from PIL import Image

startTime = time.time()

sizes = []
crcList = []
hashes = []
traitsData = []
itertoolsList = []
traits = os.listdir('Traits')

def runTimeInfo(pointInTime):
    if pointInTime == 'start':
        print(f"Bot started on: {datetime.datetime.now().replace(microsecond = 0)}")
    elif pointInTime == 'end':
        endTime = round(time.time() - startTime)
        print(f"Bot finished. Runtime: {endTime}s")

def desiredNFTCounts():
    desiredNFTs = 1
    for trait in traitsData:
        desiredNFTs = desiredNFTs * len(trait)
    print(f"Now creating {desiredNFTs} unique NFT images...")
    return desiredNFTs

def hashNFT(filePathName):
    with Image.open(filePathName) as img:
        hash = str(imagehash.average_hash(img))
    return hash

def getTraitData():
    for tIndex in range(0, len(traits)):
        variationData = []
        clonedHashes = []
        subItertoolsList = []
        variations = os.listdir(os.path.join('Traits', traits[tIndex]))
        
        for vIndex in range(0, len(variations)):
            variationPath = os.path.join('Traits', traits[tIndex], variations[vIndex])
            hash = hashNFT(variationPath)

            subItertoolsList.append(Image.open(variationPath))

            clonedHashes.append(hash)

        for hash in clonedHashes:
            percentOfVariation = round(100*clonedHashes.count(hash) / len(variations))
            data = [hash, percentOfVariation]

            if data not in variationData:
                variationData.append(data)
        
        itertoolsList.append(subItertoolsList)
        traitsData.append(variationData)

def saveTraitStackAsNFT(workingTraits, filePathName): 
    stackOfLayers = workingTraits[0]
    for img in range(1, len(workingTraits)):
        traitToLayer = workingTraits[img]
        stackOfLayers.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))
    stackOfLayers.save(filePathName, 'PNG')


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
    desiredNFTCounts()
    combinationList = itertools.product(*itertoolsList)

    for nftNumber, workingTraits in enumerate(combinationList):
        filePathName = f'NFTs\\Tin Woodman #{nftNumber+1}.PNG'

        stackOfLayers = Image.new('RGBA', (500, 500))
        for img in workingTraits:
            stackOfLayers.paste(img, (0,0), img.convert('RGBA'))
        stackOfLayers.save(filePathName, 'PNG')


    # remove duplicates
    for nft in os.listdir('NFTs'):
        filePathName = f'NFTs\\{nft}'
        size = os.path.getsize(filePathName)
        if (size in sizes):
            crcValue = cyclicRedundancyCheckOnNFT(filePathName)
            if (crcValue in crcList):
                hash = hashNFT(filePathName)
                if (hash in hashes):
                    os.remove(filePathName)
            else:
                addNewSizeCRCandHash(filePathName)
        else:
            addNewSizeCRCandHash(filePathName)

runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')