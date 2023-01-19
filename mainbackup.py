import firebase_admin# <--- Firebase shiz
from firebase_admin import credentials, firestore #<---- Firebase shiz
import requests #<--- to get webpages in their html form
from bs4 import BeautifulSoup #<-- to parse html and find specific elements
from datetime import datetime #<-- so i can write the time  of each updat the Firebase server

#These are all just setup variables for different parts of the code
cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
f = open("listNYSE.txt")
lines = f.readlines()

def updateFirebase(stock): #input stock name, get a value, and Peg, and the upload this to Firebase. This needs to check that this data exists first, or it will run into errors
    if type(stock) == str:
        value_of_stock = 0
        Peg_of_stock = ""
        urlvalue = "https://finance.yahoo.com/quote/" + stock +  "?p=GME&.tsrc=fin-srch"
        urlstats = "https://finance.yahoo.com/quote/" + stock + "/key-statistics?p=" + stock
        requestvalue = requests.get(urlvalue)
        requeststats = requests.get(urlstats)
        soupvalue = BeautifulSoup(requestvalue.content, "html.parser")
        soupstats = BeautifulSoup(requeststats.content, "html.parser")
        if soupvalue.find("span", class_="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"):
            value_of_stock = soupvalue.find("span", class_="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)").get_text()
        else:
            print(stock + "not found")
        if len(soupstats.findAll("td", class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")) != 0:
            Peg_of_stock = soupstats.findAll("td", class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[4].get_text()
        else:
            print(stock + "PEG not found")
        if value_of_stock != 0 and Peg_of_stock != "":
            document = db.collection("root").document(stock)
            document.set({
                "value": value_of_stock,
                "PEG 5 yr expected" : Peg_of_stock,
                "Time" : datetime.now().strftime("%H:%M:%S")
                })
        else:
            print("Something went wrong")


def getTop30() : # To get a list of the top 30 companies on the NYSE, available from yahoo finance. Webscrape to get this data
    companies = []
    url = 'https://finance.yahoo.com/quote/%' + '5EDJI/components?p=%'+'5EDJI'
    request = requests.get(url)
    soup = BeautifulSoup(request.content, "html.parser").find_all("td", class_="Py(10px) Ta(start) Pend(10px)")
    for i in soup:
        companies.append(str(i.get_text()))
    return companies


def returnonlyticker(): # This is the code to remove certain items from the long list of every company on the NYSE. certain items were breaking the code, so this removes those items (They are seemingly just duplicates)
    newlist = []
    hat = "^"
    for i in lines: 
        splitter = i.removesuffix("\n")
        if hat in splitter:
            print("Duplicate")
        else:
            newlist.append(splitter)
    return newlist



def eversecondinput(lists) : # The way I was webscraping returns the Ticker and the name, so this code returns just the ticker
    newlist = []
    for i in lists:
        if lists.index(i) % 2 == 0:
            newlist.append(i)
    return newlist
    

def full_send_of_30() : # command to send all of those 
    for i in eversecondinput(getTop30()):
        updateFirebase(i)

def full_send_of_all_on_market():
    for i in returnonlyticker():
        updateFirebase(i)

full_send_of_all_on_market()