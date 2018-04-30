import urllib.request
import webbrowser
import subprocess
import threading
import time
import timeit
import newlib

def wrapper(function, arg):
    'returns an object of the function together with its arguments'
    def wrapped():
        return function(arg)
    return wrapped

def first200chars(address):
    #hs = {"User-Agent" : "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}   # , headers = hs in req
    req = urllib.request.Request(address)
    print (urllib.request.urlopen(req).read())
# one of these two functions are used to actually create the internet connection
def browser_function(address):
    site = webbrowser.open(address)
    return site

# start tshark before connections are opened
def capture_pkts(tshark_args):
    def run_tshark(tsharkargs):
        subprocess.run(tsharkargs)
    threadObj = threading.Thread(target=run_tshark, args=tshark_args)
    threadObj.start()

# make connections to be stored by tshark, and measure connection times
def measure_connections(url_list, use_browser=False):
    urls_read, success_http_try, invalid_url = 0, 0, 0
    with open(url_list) as list:
        for line in list:
            urls_read += 1
            url_to_test = line[line.find(",") + 1:]
            try:
                url_to_test = "http://" + url_to_test
                print("\nAccessing: " + url_to_test)        # the url of the website accessed
                if use_browser == True:
                    wrapped = wrapper(browser_function, url_to_test)
                else:
                    wrapped = wrapper(first200chars, url_to_test)
                newlib.read_page(url_to_test)
                success_http_try += 1
            except:
                print("Invalid url: " + url_to_test )
                invalid_url += 1
            if urls_read >= 1000:
                break
            if urls_read >=10 and use_browser==True:
                break
    print(success_http_try,invalid_url)


def process_capt_pkts(proc_tshark_args):
    with open("results.txt","w") as txtfile:
        subprocess.run(proc_tshark_args, stdout=txtfile)

if __name__ == "__main__":
    newlib.read_page("https://stackoverflow.com")
    print("it works")


#
