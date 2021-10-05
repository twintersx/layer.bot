import os, socket, struct
from io import BytesIO, TextIOBase
from random import choice
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash
from itertools import chain

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

        unhashedPaths.append(variationPath)

        traitToLayer = Image.open(variationPath)
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))

    return imageStack, unhashedPaths

def convertImagesToBytes(image):
    imageByteArray = BytesIO()
    image.save(imageByteArray, format='PNG')
    imageByteArray = imageByteArray.getvalue()
    return imageByteArray

def receiveImage(s):
    def recv_msg(s):
        raw_msglen = recvall(s, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall(s, msglen)

    def recvall(s, n):
        data = bytearray()
        while len(data) < n:
            packet = s.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    return Image.open(BytesIO(recv_msg(s)))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock)
    desiredNFTs = desiredNFTCounts()

    i = 1
    while len(nftList) < desiredNFTs: #change this back to len(nftList)

        imageStack, unhashedPaths = generateRandomStack()
        if not any(imageStack in l for l in nftList):

            hashedVariations = []
            for path in unhashedPaths:
                hashedVariations.append(hashNFT(path))
            
            filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
            imageStack.save(filePathName, 'PNG')
            nftList.append(list(chain([imageStack, hashNFT(filePathName)], hashedVariations)))
            i += 1


        if socketType == 'server':

            imageReceived = receiveImage(s)
            while imageReceived is not None:  
                if isinstance(imageReceived, Image.Image):
                    if not any(imageReceived in img for img in nftList):

                        hashedVariations = []
                        while len(hashedVariations) < len(traits):
                            variationHash = s.recv(16).decode()
                            hashedVariations.append(variationHash)

                        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
                        imageReceived.save(filePathName, 'PNG')
                        nftList.append(list(chain([imageStack, hashNFT(filePathName)], hashedVariations)))
                        i += 1
                        break


        elif socketType == 'client':

            for imageHashList in nftList:
                imageByte = convertImagesToBytes(imageHashList[0])
                packedData = struct.pack('>I', len(imageByte)) + imageByte
                sock.send(packedData)

                for hashIndex in range(1, len(imageHashList)):
                    sock.send(imageHashList[hashIndex].encode())

    sock.close()

    nftDir = os.listdir('NFTs')
    testhashes = []
    for i, nft in enumerate(nftDir):
        nftPath = os.path.join('NFTs', nft)
        hash = hashNFT(nftPath)
        if hash not in testhashes:
            testhashes.append(hash)
        else:
            print("FOUND DUPLICATE, IM SORRY :( this value:", i)

    # iterate over hashes in each imageIndex, if hash exists in getTraitData, append the percentage value after it. Multiply all percentages together as you iterate to get rarity percentage. 
    # then list(chain(imageIndex, filepath, name of nft, hash of nft, newly hashed list with percentage values, rarity percentage, base cost of NFT divided by rarity of NFT (this is the final cost of NFT, the smaller the percentage the higher the price)))
    # create column names and add to excel spreadsheet
    # use this large list of data to fill in an excel spreadsheet for reference but use the list(chain) to actually list nfts on opensea


runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')