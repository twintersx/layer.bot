# pip install speedtest-cli pillow imagehash

import webbrowser as wb
import pyautogui as pag
import PIL.ImageGrab as pxl
from textwrap import dedent
from itertools import chain
from time import time, sleep
from datetime import datetime 
from random import shuffle
import os, socket, csv, ctypes, win32clipboard, struct, pickle

#pag.displayMousePosition()

finals = []
layer0Name = 'Containment Field'
numOfCollections = 1
collection = 'TinMania!' 
traits = os.listdir('traits')
BUFFER_SIZE = 4096

# --- Setup Functions --- #
def getListFromFile():
    with open('nfts - final.csv', mode = 'r') as nftFile:
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
            finals.append(rowData)

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
def send_file(sock):
    pickledList = pickle.dumps(finals)
    packedData = struct.pack('>I', len(pickledList)) + pickledList
    sock.send(packedData)

def receive_file(s):
    pickledPackadge = receivePackadge(s)
    if pickledPackadge is not None:
        receivedList = pickle.loads(pickledPackadge)
        with open('nfts - final.csv', mode = 'w', newline = '') as dataFile:
            writer = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
            writer.writerow(columnTitles)
            writer.writerows(receivedList)

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

def timeCheck(upStart, ti):
    deltaT = time() - upStart
    if deltaT > 60:
        pag.hotkey('f5')   
        sleep(10)
        ti += 1
    return 'continuous', ti

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
    path = os.path.realpath(os.path.join(os.getcwd(), "finals", name + '.PNG'))
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
        click('imageBox', 2.5)
        pag.write(path, interval=0.02)
        sleep(1.5)
        pag.press('enter')
        sleep(0.75)
        # Enter name
        tab(2, 0.2)
        pag.write(name, interval=0.002)
        
        # Enter description
        tab(3, 0.1)
        pag.write(description, interval=0.001)
        sleep(0.5)

        # Type collection name
        tab(1, 0.25) 
        pag.write(collection, interval=0.003)
        sleep(2)
        tab(1, .5)
        pag.press('enter')
        sleep(0.5)
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
            if rarityScoreIndex-3 == traitIndex-1:        
                break           
            pag.press('enter')
            pag.hotkey('shift', 'tab')      
            pag.hotkey('shift', 'tab')          
            loopCount += 1  #always one more than traits listed
        tab(3, .1)
        pag.press('enter')
        sleep(0.5)

        # Select Polygon network
        tab(loopCount + 6, 0.2)
        pag.press('enter')
        sleep(0.5)

        # Complete listing (finish minting)
        tab(3, 0.2)
        pag.press('enter')

        # Wait until minting is complete and return to collection page
        sellColors = pxl.grab().load()[1440, 220]
        ti = 0
        while sellColors[0] > 33:
            state, ti = timeCheck(upStart, ti)
            if ti >> 0:
                state = "restart"
                break
            pag.press('esc')
            sellColors = pxl.grab().load()[1440, 220]
            sleep(0.25)

        if mint == 'mint': 
            break

        # Press Sell NFT
        click('sell', 1)

        ti = 0
        polyColors = pxl.grab().load()[215, 436]
        while polyColors[0] > 200:
            state, ti = timeCheck(upStart, ti)
            if ti >> 0:
                state = "restart"
                break
            polyColors = pxl.grab().load()[215, 436]
            sleep(0.25)

        # Enter listing price
        pag.write(price, interval=0.01)
        sleep(0.5)

        ti = 0
        compListColors = pxl.grab().load()[205, 825]
        while compListColors[0] > 33:
            state, ti = timeCheck(upStart, ti)
            if ti >> 0:
                state = "restart"
                break
            compListColors = pxl.grab().load()[205, 825]
            sleep(0.25)

        # Complete Listing on sell page
        click('completeListing', 2)

        ti = 0
        sign1Colors = pxl.grab().load()[660, 600]
        while sign1Colors[0] > 33:
            state, ti = timeCheck(upStart, ti)
            if ti >> 0:
                state = "restart"
                break
            sign1Colors = pxl.grab().load()[660, 600]
            sleep(0.25)

        # 1st sign on OpenSea
        click('sign1', 0.5)

        ti = 0
        sign2Colors = pxl.grab().load()[1780, 550]
        while sign2Colors[0] > 33:
            state, ti = timeCheck(upStart, ti)
            if ti >> 0:
                state = "restart"
                break
            sign2Colors = pxl.grab().load()[1780, 550]
            sleep(0.25)

        # 2nd sign on Metamask
        click('sign2', 3.5)
        break

    if internet() and state == 'continuous':
        pag.hotkey('ctrl', 'l')
        sleep(0.1)
        pag.hotkey('ctrl', 'c')

        win32clipboard.OpenClipboard()
        url = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard() 

        paths = url.split('/')
        for i, path in enumerate(paths):
            if '0x' in path:
                contractAddress = path
                token_id = paths[i+1]

                finals[nftIndex][contractIndex] = contractAddress
                finals[nftIndex][token_idIndex] = token_id

                if mint == 'mint':
                    uploadState = 'minted only'
                else:
                    uploadState = 'yes'
                    
    finals[nftIndex][listedIndex] = uploadState

    pag.hotkey('ctrl', 'w')            
    if nftIndex != len(finals) - 1:
        wb.open('https://opensea.io/asset/create', new = 2)
        sleep(3)

    return uploadState, state

def mintOnOpenSea(columnTitles):
    current = len(os.listdir("finals"))
    listedIndex = columnTitles.index("Listed on OpenSea?")
    idIndex = columnTitles.index("NFT ID")
    descIndex = columnTitles.index("Description")

    """uploads = os.listdir("uploads")
    uploads = [s.replace(".PNG", "") for s in uploads]"""
    
    ip = getIP()
    towerIP = '192.168.1.3'     
    workIP = '192.168.1.7' # personal is '192.168.1.5' 

    """sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s, socketType = initializeSocket(sock, towerIP) # set server (receiving)
    if ip == towerIP:
        receive_file(s)
    elif ip == workIP:
        send_file(sock)"""
    socketType = 'server'

    pcUploadList = []
    if ip == workIP:
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
    for nftData in finals:  
        if nftData[listedIndex] == 'minted only' or nftData[listedIndex] == 'yes':
            listed += 1
    count = round(current - listed) # half if using two computers to upload #round((current - listed) / 2)
    print(f'Now minting (and listing) {count} between {init} and {fin}...')

    wb.open('https://opensea.io/asset/create', new=2)
    messageBox() 
    shuffle(finals)  

    i = listed
    for nftIndex, nftRow in enumerate(finals):
        mint = ''
        if i >> count: break
        """if nftRow[0] not in pcUploadList: continue
        if nftRow[nameIndex] not in uploads: mint = 'mint'"""

        nftRow[descIndex] = '**' + nftRow[descIndex]
        nftRow[descIndex] = nftRow[descIndex].replace('\n', '**\n', 1)

        if nftRow[listedIndex] == 'no':
            uploadState = 'no'
            while uploadState == 'no':
                uploadState, state = listNFT(nftRow, nftIndex, columnTitles, mint)
                if state == 'restart':
                    break

            """if socketType == 'client':
                pickledList = pickle.dumps(finals[nftIndex])
                packedData = struct.pack('>I', len(pickledList)) + pickledList
                sock.send(packedData)"""

            """if socketType == 'server':
                pickledPackadge = receivePackadge(s)
                if pickledPackadge is not None:
                    receivedList = pickle.loads(pickledPackadge)
                    for nftIndex, nftRow in enumerate(finals):
                        if receivedList[idIndex] in nftRow:
                            finals[nftIndex] = receivedList"""

            # indent this once more to fit under server only
            with open('nfts - final.csv', mode = 'w', newline = '') as dataFile:
                writer = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
                writer.writerow(columnTitles)
                writer.writerows(finals)
                i += 1

    runTimeInfo('upload') 
    
# --- Setup --- #
getListFromFile()
columnTitles = titleRow() 

# --- Main --- #
mintOnOpenSea(columnTitles)