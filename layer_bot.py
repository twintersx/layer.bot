import os, random, imagehash, datetime, zlib
from PIL import Image

traits = os.listdir('Traits')

def runTimeInfo():
    print(f"Bot started on: {datetime.datetime.now().replace(microsecond = 0, second = 0)}")

def desiredNFTCounts():
    variations = 1
    for t in traits:
        variations = variations * len(os.listdir(os.path.join('Traits', t)))
    print(f"Now creating {variations} unique NFT images...")
    return(variations)

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

def hashNFT(filePathName):
    with Image.open(filePathName) as img:
        hash = str(imagehash.average_hash(img))
    return hash

def currentNFTs():
    return(len(os.listdir('NFTs')))

def main():
    i = 1
    sizes = []
    crcList = []
    hashes = []
    desiredNFTs = desiredNFTCounts()
    while currentNFTs() < desiredNFTs:
        filePathName = f'NFTs\\{i}.PNG'
        saveTraitStackAsNFT(filePathName)

        size = os.path.getsize(filePathName)
        crcValue = cyclicRedundancyCheckOnNFT(filePathName)
        hash = hashNFT(filePathName)

        if (size in sizes) and (crcValue in crcList) and (hash in hashes):
            os.remove(filePathName)
        else:
            sizes.append(size)
            crcList.append(crcValue)
            hashes.append(hash)
            i += 1           

runTimeInfo()
main()