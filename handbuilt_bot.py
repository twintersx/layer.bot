import webbrowser as wb
import pyautogui as pag
import PIL.ImageGrab as pxl
from textwrap import dedent
from time import time, sleep
from random import shuffle
import os, socket, csv, ctypes, win32clipboard

handbuilts = []
headers = ["NFT No","Name","Listing Price","Description","Layer","Trait","Listed on OpenSea?","Contract Address","token_id"]
numOfCollections = 1
collection = 'TinMania!' 

# --- Get nfts[] --- #
def createHandbuiltData():
    with open('nfts - handbuilt.csv', mode = 'r') as nftFile:
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
            handbuilts.append(rowData)

    traitI = headers.index('Trait')
    traitNames = os.listdir("handbuilts")

    for i, data in enumerate(handbuilts):
        try:
            oldPath = os.path.join(os.getcwd(), 'handbuilts', traitNames[i])
            newPath = os.path.join(os.getcwd(), 'handbuilts', data[1] + '.PNG')
            os.rename(oldPath, newPath)
        except:
            print(f"{oldPath} cannot be found.")
    
        traitNames[i] = traitNames[i].replace(".png", "")
        traitNames[i] = ''.join(c for c in traitNames[i] if not c.isdigit()).strip().title()
        handbuilts[i][traitI] = traitNames[i]

    with open('nfts - handbuilt.csv', mode = 'r+', newline = '') as dataFile:
        nftCSV = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
        nftCSV.writerow(headers)
        nftCSV.writerows(handbuilts)

# --- Mint/Upload Functions --- #
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

    elif button == 'auction':
        pag.click(695, 467)

    elif button == 'info':
        pag.click(859, 962)
    
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

def listNFT(i, data, headers):
    name = data[1]
    path = os.path.realpath(os.path.join(os.getcwd(), "handbuilts", name + '.PNG'))
    description = data[headers.index('Description')]
    trait = data[headers.index('Trait')]
    price = str(data[headers.index('Listing Price')])
    listedIndex = headers.index("Listed on OpenSea?")        
    contractIndex = headers.index("Contract Address")
    token_idIndex = headers.index("token_id")

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
        pag.write("Handbuilt") 
        tab(1, 0.1)
        pag.write(trait)       
        tab(2, 0.1)         
        loopCount += 1  #always one more than traits listed
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

                handbuilts[i][contractIndex] = contractAddress
                handbuilts[i][token_idIndex] = token_id

                uploadState = 'yes'
                    
    handbuilts[i][listedIndex] = uploadState

    pag.hotkey('ctrl', 'w')            
    wb.open('https://opensea.io/asset/create', new = 2)
    sleep(3)

    return uploadState, state

def mintOnOpenSea():
    listedI = headers.index("Listed on OpenSea?")

    wb.open('https://opensea.io/asset/create', new=2)
    messageBox() 
    shuffle(handbuilts)  

    for i, data in enumerate(handbuilts):

        if data[listedI] == 'no':
            uploadState = 'no'
            while uploadState == 'no':
                uploadState, state = listNFT(i, data, headers)
                if state == 'restart':
                    break

            # indent this once more to fit under server only
            with open('nfts - handbuilt.csv', mode = 'w', newline = '') as dataFile:
                writer = csv.writer(dataFile, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
                writer.writerow(headers)
                writer.writerows(handbuilts)

#createHandbuiltData()
# --- Main --- #
mintOnOpenSea(headers)