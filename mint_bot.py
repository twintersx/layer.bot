from PIL import Image
from zlib import crc32
from numpy import save
import webbrowser as wb
import pyautogui as pag
from ctypes import windll
from imagehash import phash
import PIL.ImageGrab as pxl
from textwrap import dedent
from itertools import chain
from time import time, sleep
from datetime import datetime
from random import choice, shuffle
from statistics import stdev, mean
import os, socket, csv, ctypes, win32clipboard, struct, pickle, tqdm

nfts = []
layer0Name = 'Containment Field'
numOfCollections = 1
collection = 'TinMania!' 
traits = os.listdir('traits')

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = round((int(os.path.getsize("nfts.csv")) + 1024)/1024)

# --- Setup Functions --- #
def getListFromFile():
    with open('nfts.csv', mode = 'r') as nftFile:
        reader = csv.reader(nftFile, delimiter = ',')
        next(reader)
        for row in reader:
            rowData = []
            for x in row:
                try: 
                    if int(x): 
                        item = int(x)
                    elif float(x): 
                        item = float(x)
                except: 
                    item = x
                rowData.append(item)
            nfts.append(rowData)

def titleRow():
    columnTitles = ['NFT No', "File Path", "Name", "Size (KB)", "CRC Value", "NFT ID"]
    for trait in traits:
        trait = ''.join(i for i in trait if not i.isdigit()).title().replace('_', '')
        columnTitles = list(chain(columnTitles, [trait, f"{trait} ID", f"{trait} %"]))
    
    columnTitles = list(chain(columnTitles, ["Rarity Score", "Listing Price", "Rarity Type", "Rarity Counts", "Description", "Listed on OpenSea?", "Contract Address", "token_id"]))
    return columnTitles

def getIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return(ip)

def initializeSocket(sock, serverIP):
    if getIP() == serverIP:
        socketType = 'server'
        sock.bind(('0.0.0.0', 1200))
        sock.listen(10)
        print ("Waiting for Client connection...")
        s, addr = sock.accept()
        print ("Client connected:", addr)
    else:
        socketType = 'client'
        sock.connect((serverIP, 1200))
        s = None
    return s, socketType

def runTimeInfo(pointInTime):
    startTime = time()

    if pointInTime == 'start':
        print(f"Start time: {datetime.now().replace(microsecond = 0)}")

    elif pointInTime == 'nft_creation':
        endTime = round(time() - startTime)
        print(f"This process took: {endTime}s")

    elif pointInTime == 'upload':
        endTime = round((time() - startTime)/60)
        print(f"Upload complete! Total upload time: {endTime} mins")

# --- Mint/Upload Functions --- #
def send_file(filename, s):
    filesize = os.path.getsize(filename)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, mode = 'rb') as dataFile:
        while True:
            bytes_read = dataFile.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))

def receive_file(filename, s):
    received = s.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as dataFile:
        while True:
            bytes_read = s.recv(BUFFER_SIZE)
            if not bytes_read:    
                break
            dataFile.write(bytes_read)
            progress.update(len(bytes_read))

def messageBox():
    message = ("""
                Check that your Metamask wallet is connected.
                Hitting "Ok" will start the minting process...
                You need to be on https://opensea.io/asset/create
                """)
    title = "NFT Creator: \u00A1Atención!"  

    while True:
        try:
            response = ctypes.windll.user32.MessageBoxW(None, dedent(message), title, 0x1000)
            if response == 1:
                break
        except Exception as e: print(e)

def tab(count, delay):
    for _ in range(0, count):
        pag.press('tab')
        sleep(delay)

def click(button, delay):
    if button == 'imageBox':
        pag.click(725, 500)

    elif button == 'sell':
        pag.click(1450, 215)
    
    elif button == 'completeListing':
        pag.click(275, 832)

    elif button == 'sign1':
        pag.click(675, 615)

    elif button == 'sign2':
        pag.click(1825, 550)

    sleep(delay)

def internet():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def timeCheck(upStart):
    deltaT = time() - upStart
    if deltaT > 60:
        pag.hotkey('f5')   
        sleep(10)
    return 'continuous'

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

def listNFT(nftRow, nftIndex, titles, mint):
    name = nftRow[2]
    path = os.path.realpath(os.path.join(os.getcwd(), "nfts", name))
    description = nftRow[titles.index('Description')]
    backgroundIndex = titles.index(layer0Name)
    rarityScoreIndex = titles.index('Rarity Score')
    price = str(nftRow[titles.index('Listing Price')])
    listedIndex = titles.index("Listed on OpenSea?")
    contractIndex = titles.index("Contract Address")
    token_idIndex = titles.index("token_id")

    uploadState = 'no'
    upStart = time()
    state = 'continuous'
    while state == 'continuous':
        # Upload NFT via Image Box
        click('imageBox', 2.25)
        pag.write(path, interval=0.01)
        sleep(.75)
        pag.press('enter')
        sleep(1)

        # Enter name
        tab(2, 0.2)
        pag.write(name, interval=0.002)
        
        # Enter description
        tab(3, 0.2)
        pag.write(description, interval=0.002)
        sleep(1)

        # Type collection name
        tab(1, 0.2) 
        pag.write(collection, interval=0.005)
        sleep(2)
        tab(1, .5)
        pag.press('enter')
        sleep(1)
        tab(2 + numOfCollections, 0.5) 

        # Enter Trait info
        pag.press('enter')
        sleep(0.5)
        loopCount = 1   
        for traitIndex in range(backgroundIndex, rarityScoreIndex-2, 3):
            if nftRow[traitIndex+1] == 8000000000000000:
                continue
            pag.write(titles[traitIndex])
            tab(1, 0.1)
            pag.write(nftRow[traitIndex])
            tab(1, 0.1)
            if rarityScoreIndex-3 == traitIndex:
                break
            pag.press('enter')
            pag.hotkey('shift', 'tab')
            sleep(0.1)
            pag.hotkey('shift', 'tab')
            sleep(0.1)
            loopCount += 1  #always one more than traits listed
        tab(3, .25)
        pag.press('enter')
        sleep(.5)

        # Select Polygon network
        tab(loopCount + 6, 0.25)
        pag.press('enter')
        sleep(0.5)

        # Complete listing (finish minting)
        tab(3, 0.2)
        pag.press('enter')

        # Wait until minting is complete and return to collection page
        sellColors = pxl.grab().load()[1440, 220]
        while sellColors[0] > 33:
            state = timeCheck(upStart)
            pag.press('esc')
            sellColors = pxl.grab().load()[1440, 220]
            sleep(0.5)

        if mint == 'mint': 
            break

        # Press Sell NFT
        click('sell', 1.5)

        polyColors = pxl.grab().load()[215, 436]
        while polyColors[0] > 200:
            state = timeCheck(upStart)
            polyColors = pxl.grab().load()[215, 436]
            sleep(0.25)

        # Enter listing price
        pag.write(price, interval=0.01)
        sleep(0.5)

        compListColors = pxl.grab().load()[205, 825]
        while compListColors[0] > 33:
            state = timeCheck(upStart)
            compListColors = pxl.grab().load()[205, 825]
            sleep(0.25)

        # Complete Listing on sell page
        click('completeListing', 2)

        sign1Colors = pxl.grab().load()[660, 600]
        while sign1Colors[0] > 33:
            state = timeCheck(upStart)
            sign1Colors = pxl.grab().load()[660, 600]
            sleep(0.25)

        # 1st sign on OpenSea
        click('sign1', 0.5)

        sign2Colors = pxl.grab().load()[1780, 550]
        while sign2Colors[0] > 33:
            state = timeCheck(upStart)
            sign2Colors = pxl.grab().load()[1780, 550]
            sleep(0.5)

        # 2nd sign on Metamask
        click('sign2', 3.5)
        break

    if internet():
        pag.hotkey('ctrl', 'l')
        sleep(0.2)
        pag.hotkey('ctrl', 'c')

        win32clipboard.OpenClipboard()
        url = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard() 

        paths = url.split('/')
        for i, path in enumerate(paths):
            if '0x' in path:
                contractAddress = path
                token_id = paths[i+1]

                nfts[nftIndex][contractIndex] = contractAddress
                nfts[nftIndex][token_idIndex] = token_id

                if mint == 'mint':
                    uploadState = 'minted only'
                else:
                    uploadState = 'yes'
                    
    nfts[nftIndex][listedIndex] = uploadState

    pag.hotkey('ctrl', 'w')            
    if nftIndex != len(nfts) - 1:
        wb.open('https://opensea.io/asset/create', new = 2)
        sleep(3)

    return uploadState

def mintOnOpenSea(columnTitles):
    current = len(os.listdir("nfts"))
    listedIndex = columnTitles.index("Listed on OpenSea?")
    nameIndex = columnTitles.index("Name")
    idIndex = columnTitles.index("NFT ID")

    uploads = os.listdir("uploads")
    uploads = [s.replace(".PNG", "") for s in uploads]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    towerIP = '192.168.1.3'
    s, socketType = initializeSocket(sock, towerIP)
    
    ip = getIP()

    filename = "nfts.csv"
    if ip == towerIP:
        send_file(filename, s)
    elif ip != towerIP:
        receive_file(filename, sock)

    pcUploadList = []
    if ip == towerIP:
        init = 1
        fin = round(current/2)
        for i in range(init, fin+1):
            pcUploadList.append(i)
    else:
        init = round(current/2) + 1
        fin = current
        for i in range(init, fin):
            pcUploadList.append(i)

    listed = 0
    for nftData in nfts:
        if nftData[listedIndex] == 'minted only' or nftData[listedIndex] == 'yes':
            listed += 1
    count = round((current - listed) / 2) # half if using two computers to upload
    print(f'Now minting (and listing) {count} between {init} and {fin}...')

    wb.open('https://opensea.io/asset/create', new=2)
    messageBox() 
    shuffle(nfts)  

    i = listed
    for nftIndex, nftRow in enumerate(nfts):
        mint = ''
        if i >> count: break
        if nftRow[0] not in pcUploadList: continue
        if nftRow[nameIndex] not in uploads: mint = 'mint'

        if nftRow[listedIndex] == 'no':
            uploadState = 'no'
            while uploadState == 'no':
                uploadState = listNFT(nftRow, nftIndex, columnTitles, mint)

            if socketType == 'client':
                pickledList = pickle.dumps(nfts[nftIndex])
                packedData = struct.pack('>I', len(pickledList)) + pickledList
                sock.send(packedData)

            if socketType == 'server':
                pickledPackadge = receivePackadge(s)
                if pickledPackadge is not None:
                    receivedList = pickle.loads(pickledPackadge)
                    for nftIndex, nftRow in enumerate(nfts):
                        if receivedList[idIndex] in nftRow:
                            nfts[nftIndex] = receivedList

                with open('nfts.csv', mode = 'w', newline = '') as dataFile:
                    writer = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
                    writer.writerow(columnTitles)
                    writer.writerows(nfts)
                    i += 1

    runTimeInfo('upload') 

# --- Setup --- #
getListFromFile()
columnTitles = titleRow() 

# --- Main --- #
mintOnOpenSea(columnTitles)