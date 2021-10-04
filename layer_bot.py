import os, io, socket, struct
from random import choice
from datetime import datetime
from time import time
from PIL import Image
from imagehash import average_hash
import pickle

startTime = time()
socketType = ''
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
    else:
        socketType = 'client'
        sock.connect(('192.168.1.5', 1200))
        s = None

    return s, socketType

def byteArrayToSend():
    nftListByteArray = io.BytesIO()
    nftListByteArray = nftList
    nftListByteArray = nftListByteArray.getvalue()
    return struct.pack('>I', len(nftListByteArray)) + nftListByteArray

def generateRandomStack():
    imageStack = Image.new('RGBA', (500, 500))
    for trait in traits:
        variationDir = os.path.join('Traits', trait)
        randomVariation = choice(os.listdir(variationDir))
        variationPath = os.path.join(variationDir, randomVariation)

        traitToLayer = Image.open(variationPath)
        imageStack.paste(traitToLayer, (0,0), traitToLayer.convert('RGBA'))

    return imageStack

def receivedMessage(s):
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

    return io.BytesIO(recv_msg(s))

def main():
    desiredNFTs = desiredNFTCounts()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock)
    timeOfLastNFT = 0

    i = 1
    while len(nftList) < desiredNFTs:
        filePathName = f'NFTs\\Tin Woodman #{i}.PNG'

        imageStack = generateRandomStack()
        if imageStack not in nftList:
            nftList.append(imageStack)
            imageStack.save(filePathName, 'PNG')
            timeOfLastNFT = time()
            i += 1


        if (socketType == 'server') and (time() > timeOfLastNFT + 10):
            clientImageList = pickle.loads(receivedMessage(s))
            for image in clientImageList:
                if image not in nftList:
                    nftList.append(imageStack)
                    imageStack.save(filePathName, 'PNG')
                    timeOfLastNFT = time()
                    i += 1

        if socketType == 'client':
            data = pickle.dumps(byteArrayToSend())
            sock.send(data)

runTimeInfo('start')
getTraitData()
main()
runTimeInfo('end')