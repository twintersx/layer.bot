import os, io, socket, struct
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
    return imageStack

def cyclicRedundancyCheckOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def currentNFTs():
    return(len(os.listdir('NFTs')))

def inputPCSocketType():
    while True:
        socketType = input("Is this PC a 'client' or the 'server': ")
        if socketType == 'client' or socketType == 'server':
            return socketType
        print("Invalid entry")

def getIncomingHash(s):
    while True:
        hash = s.recv(16).decode()
        if not hash: return None
        return hash

def saveIncomingHash(filePathName, s):
    def recv_msg(c):
        raw_msglen = recvall(c, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall(c, msglen)

    def recvall(c, n):
        data = bytearray()
        while len(data) < n:
            packet = c.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    imageStack = Image.open(io.BytesIO(recv_msg(s)))
    imageStack.save(filePathName, 'PNG')
    sizes.append(os.path.getsize(filePathName))
    crcList.append(cyclicRedundancyCheckOnNFT(filePathName))
    hashes.append(hashNFT(filePathName))

def server(sock):
    sock.bind(('0.0.0.0', 1200))
    sock.listen(1)
    return (sock.accept())

def sendHash(sock, hash, imageStack):
    
    sock.connect(('192.168.1.5', 1200))

    hashToSend = bytes(f'{hash}', 'utf-8')
    sock.sendall(hashToSend)

    imageByteArr = io.BytesIO()
    imageStack.save(imageByteArr, format='PNG')
    imageByteArr = imageByteArr.getvalue()

    msg = struct.pack('>I', len(imageByteArr)) + imageByteArr
    sock.sendall(msg)
    
def main(socketType):
    getTraitData()
    desiredNFTs = desiredNFTCounts()

    i = 1
    while currentNFTs() < desiredNFTs:
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        sock = socket.socket()


        if socketType == 'server':
            s = server(sock)
            if getIncomingHash(s) and getIncomingHash(s) not in hashes:
                saveIncomingHash(filePathName, i, s)
                i += 1
                break


        imageStack = saveTraitStackAsNFT(pickRandomTraits(), filePathName)

        size = os.path.getsize(filePathName)
        if (size in sizes):
            crcValue = cyclicRedundancyCheckOnNFT(filePathName)
            if (crcValue in crcList):
                hash = hashNFT(filePathName)
                if (hash in hashes):
                    os.remove(filePathName)
            else:
                sizes.append(size)
                crcList.append(crcValue)
                hash = hashNFT(filePathName)
                hashes.append(hash)
                if socketType == 'client':
                    sendHash(sock, hash, imageStack)
                i += 1
        else:
            sizes.append(size)
            crcList.append(cyclicRedundancyCheckOnNFT(filePathName))
            hashes.append(hashNFT(filePathName))
            if socketType == 'client':
                    sendHash(sock, hash, imageStack)
            i += 1


runTimeInfo('start')
main(inputPCSocketType())
runTimeInfo('end')