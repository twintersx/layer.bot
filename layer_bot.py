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

def getServerIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def getIncomingHash(sock):
    while True:
        s, addr = sock.accept()
        hash = s.recv(16).decode()
        if not hash: 
            print("None hash recved: ", 'None')
            return None 
        print("hash recved: ", hash)
        return s, hash

def saveIncomingHash(filePathName, s):
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
    print("image byte object data recieved")
    imageStack.save(filePathName, 'PNG')
    sizes.append(os.path.getsize(filePathName))
    crcList.append(cyclicRedundancyCheckOnNFT(filePathName))
    hashes.append(hashNFT(filePathName))

def sendHash(sock, hash, imageStack):
    imageByteArr = io.BytesIO()
    imageStack.save(imageByteArr, format='PNG')
    imageByteArr = imageByteArr.getvalue()
    structToSend = struct.pack('>I', len(imageByteArr)) + imageByteArr
    imgHash = [hash, structToSend]
    imgHashListToSend.append(imgHash)

    sock.sendall(bytes(imgHashListToSend))

def initializeSocket(sock):
    if getServerIP() == '192.168.1.5':
        socketType = 'server'
        sock.bind(('0.0.0.0', 1200))
        sock.listen(10)
    else:
        socketType = 'client'
        sock.connect(('192.168.1.5', 1200))

    return socketType

def main():
    desiredNFTs = desiredNFTCounts()
    sock = socket.socket()
    socketType = initializeSocket(sock)

    i = 1
    while currentNFTs() < desiredNFTs:
        if socketType == 'server':
            s, hash = getIncomingHash(sock)
            if hash not in hashes and hash != 'None':
                saveIncomingHash(f'NFTs\\Tin Woodman #{i}.PNG', s)
                i += 1

        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'
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
            hash = hashNFT(filePathName)
            hashes.append(hash)
            if socketType == 'client':
                sendHash(sock, hash, imageStack)
            i += 1

runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')