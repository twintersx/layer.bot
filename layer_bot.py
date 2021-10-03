import os, io, socket, struct
from random import choice
from zlib import crc32
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash

startTime = time()
socketType = ''
sizes = []
crcList = []
hashes = []
traitsData = []
imgHashListToSend = []
traits = os.listdir('Traits')

def runTimeInfo(pointInTime):
    if pointInTime == 'start':
        print(f"Bot started on: {datetime.now().replace(microsecond = 0)}")
    elif pointInTime == 'end':
        endTime = round(time() - startTime)
        print(f"Bot finished. Runtime: {endTime}s")

def getServerIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

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
    else:
        socketType = 'client'
        sock.connect(('192.168.1.5', 1200))

    return s, socketType

def currentNFTs():
    return(len(os.listdir('NFTs')))

def hashNFT(filePathName):
    with Image.open(filePathName) as img:
        hash = str(average_hash(img))
    return hash

def cyclicRedundancyCheckOnNFT(filePathName):
    prev = 0
    for eachLine in open(filePathName, "rb"):
        prev = crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def saveTraitStackAsNFT(filePathName): 
    randomTraits = []  
    for trait in traits:
        variationDir = os.path.join('Traits', trait)
        randomVariation = choice(os.listdir(variationDir))
        variationPath = os.path.join(variationDir, randomVariation)
        randomTraits.append(Image.open(variationPath))

    imageStack = Image.new('RGBA', (500, 500))
    for img in range(0, len(randomTraits)):
        traitToLayer = randomTraits[img]
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))
    imageStack.save(filePathName, 'PNG')
    return imageStack

def saveIncomingImage(filePathName, s):
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

    imageStack = Image.open(io.BytesIO(recv_msg(s)))
    imageStack.save(filePathName, 'PNG')

def sendImage(sock, imageStack):
    imageByteArr = io.BytesIO()
    imageStack.save(imageByteArr, format='PNG')
    imageByteArr = imageByteArr.getvalue()
    structToSend = struct.pack('>I', len(imageByteArr)) + imageByteArr
    imgHashListToSend.append(hash + structToSend)
    with open('your_file.txt', 'w') as f:
        for item in imgHashListToSend:
            f.write("%s\n" % item)
    fileToSend = open('your_file.txt', 'r')
    content = fileToSend.read()
    sock.send(content.encode())

def main():
    desiredNFTs = desiredNFTCounts()
    sock = socket.socket()
    s, socketType = initializeSocket(sock)

    i = 1
    while currentNFTs() < desiredNFTs:
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        if socketType == 'server':
            saveIncomingImage(filePathName, s)
            
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
                    i += 1
            else:
                sizes.append(size)
                crcList.append(cyclicRedundancyCheckOnNFT(filePathName))
                hash = hashNFT(filePathName)
                hashes.append(hash)
                i += 1

        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
        imageStack = saveTraitStackAsNFT(filePathName)

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
                    sendImage(sock, hash, imageStack)
                i += 1
        else:
            sizes.append(size)
            crcList.append(cyclicRedundancyCheckOnNFT(filePathName))
            hash = hashNFT(filePathName)
            hashes.append(hash)
            if socketType == 'client':
                sendImage(sock, hash, imageStack)
            i += 1

runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')