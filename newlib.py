import urllib.request
import subprocess
import threading
import time
from bs4 import BeautifulSoup

def read_page(address):
    # hs = {"User-Agent" : "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
    req = urllib.request.Request(address)

    soup = BeautifulSoup(urllib.request.urlopen(req).read())


    # hs = {"User-Agent" : "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}   # , headers = hs in req


    for a_tag in soup.find_all("a", href=True):
        print("href:", a_tag['href'])
        if str(a_tag['href'])[0] == "/":
            print(address + a_tag['href'])
            req_href = urllib.request.Request(address + a_tag['href'])
            try:
                print(urllib.request.urlopen(req_href).read(), "\n")
            except:
                continue
        elif str(a_tag['href'])[0] == "?":
            print(address + a_tag['href'])
            req_href = urllib.request.Request(address + a_tag['href'])
            try:
                print(urllib.request.urlopen(req_href).read(), "\n")
            except:
                continue
        else:
            try:
                req_href = urllib.request.Request(a_tag['href'])
                try:
                    print(urllib.request.urlopen(req_href).read())
                except:
                    continue
            except:
                continue








    #
