import platform
import os
import subprocess
from os.path import splitext
from collections import Counter
from flask import Flask, render_template
import threading, webbrowser

BLE = ["BluetoothDevice;->connectGatt","PAIRING_REQUEST","BluetoothDevice;->setPin","PAIRING_KEY","BluetoothGatt;->readCharacteristic","BluetoothGatt;->writeCharacteristic"]
statistics = {}

app = Flask(__name__)

@app.route("/")
def hello():

    return render_template('report.html', result=statistics)


class BreakIt(Exception): pass


def getslash():
    global slash
    if platform.system()== 'Windows':
        print('Windows platform detected..')
        slash = "\\"
    elif platform.system()== 'Linux':
        print('Unix platform detected..')
        slash = "/"
    else:  #OSX
        print('This OS is not supported yet.')
        exit()
    return slash


def decoder(dir):
    dirSMA = dir+slash+"SMALIS"

    os.popen("mkdir "+dirSMA)     # Creates folder for smali classes

    for file in os.listdir(dir):
        if file.endswith(".apk"):
            basefile = splitext(file)[0]
            #Decode the APK files into smalis, saves them in the created SMALIS folder
            decoding=subprocess.Popen("apktool d "+dir+slash+file+" -o "+dirSMA+slash+basefile, shell=True)
            decoding.wait()
    print("All files decoded")
    return


def analyser(dir,keyword):
    passedCheck = {}
    dirSMA = dir+slash+"SMALIS"
    toCheck=os.listdir(dirSMA)

    for app in toCheck:

        print('Evaluating', app)
        appChar=[]
        for item in keyword:
            try:
                for root, subFolders, files in os.walk(dirSMA+slash+app):
                    for file in files:
                        if file.endswith(".smali"):
                            with open(os.path.join(root, file), 'r') as fin:
                                for line in fin:
                                    if item in line:
                                        # print(" POSITIVE - APP: "+app+" with API call: "+item+" was found in class: "+file)
                                        appChar.append(item)
                                        passedCheck[app] = appChar
                                        raise BreakIt
            except BreakIt:
                pass
    return toCheck,passedCheck


def results(total,apps):
    all_lists = []
    print("\n===============RESULTS==================\n")
    print("\033[1;31m Total number of apps found in the SMALIS folder:\033[0;0m"+str(len(total)))
    print("\033[1;32m Total number of apps using BLE or one of the API calls: \033[0;0m"+str(len(apps)))
    print("\033[1;33m Apps Using BLE or one of the API calls: \033[0;0m"+str(apps.keys()))

    for key,value in apps.items():
        print("\n\033[1;31mAPP: "+key+"\033[0;0m")
        print(*value, sep="\n")

    for list in apps.values():
        all_lists = all_lists+list

    stats = Counter(all_lists)
    print("\nStatistics: "+str(stats))

    return stats


def report():
    port = 5000
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run(port=port, debug=False)


if __name__ == "__main__":

    print("Press D for decoding or A for analysis of decoded APKs.")
    choice = input()

    if choice == 'D' or choice == 'A':
            print("Give the ABSOLUTE PATH to the APKs. eg. C:\Windows")
            dir=input()
            slash = getslash()
            decoder(dir)

            if choice == 'A':
                print("\033[1;31m  Give the API call keyword you want to search in the APKs or Press Enter to search for BLE API calls. \033[0;0m")
                keyword = input()
                if not keyword:
                    total,apps=analyser(dir, BLE)
                else:
                    total,apps=analyser(dir, keyword)
                statistics = results(total,apps)
                statistics['Total'] = len(total)
                print("\033[1;31m Do you want to generate a statistics report? Y or N \033[0;0m")
                if input() == "Y":
                    report()
    else:
        exit()