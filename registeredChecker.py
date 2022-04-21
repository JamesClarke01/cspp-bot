from selenium import webdriver
from selenium.webdriver.common.by import By

import os

import json
from os import listdir, remove

from decouple import config

import csv

#global constants
csvPage = "https://www.tudublin.ie/socsportal/admin/index.php?object=T3JnYW5pc2F0aW9uTWVtYmVy&organisationID=MTA2NQ==&actionType=cmVhZA==&action=Ng==&method=Y3N2RXhwb3J0"

pastNumberFile = "previouslyVerifiedNumbers.json"

#csvDownloadDir = r"C:\Users\james\OneDrive - Technological University Dublin\College\CS++\DiscordBot\csvs" #must be the full path for setting selinium download dir
csvDownloadDir = os.getcwd()



USER = config('U')
P = config('P')


def setupChromeDriver():
    #selenium setup
    chromeOptions = webdriver.ChromeOptions()

    prefs = {"download.default_directory" : csvDownloadDir}

    chromeOptions.add_experimental_option("prefs", prefs) #set the default download directory

    driver = webdriver.Chrome(options=chromeOptions)

    return driver

def bypassPage1(driver):
    try:
        singleLoginButton = driver.find_element(By.CLASS_NAME, "btn-danger")
    except:
        print("Page 1 not loaded yet")
        return False

    singleLoginButton.click()

    return True

def bypassPage2(driver):

    try:
        emailBox = driver.find_element(By.ID, "username")

        passwordBox = driver.find_element(By.ID,"password")

        submitBox = driver.find_element(By.ID,"submitLogin")
    except:
        print("Page 2 not loaded yet")
        return False

    emailBox.send_keys(USER)
    passwordBox.send_keys(P)
    submitBox.click()

    return True




def waitUntilLoaded(funcThatRequiresLoaded, *args):
    """Will run function passed a defined amount of time until the function returns true or the limit is succeeded"""
    cycleWaitTime = 10000
    
    for i in range(cycleWaitTime):
        if funcThatRequiresLoaded(*args):
            print(funcThatRequiresLoaded, "successful")
            return True

        elif i == cycleWaitTime-1:
            print(funcThatRequiresLoaded, "unsuccessful")
            return False

    
def downloadCsv():

    if csvDownloaded() == True:
        print("Csv Already in folder")
        return False

    driver = setupChromeDriver()
    
    driver.get(csvPage) #open page
    
    #bypass page 1
    if not waitUntilLoaded(bypassPage1, driver):
        return False

    #bypass page 2
    if not waitUntilLoaded(bypassPage2, driver):
        return False
    
    #download csv
    if not waitUntilLoaded(csvDownloaded):
        return False

    return True

def csvDownloaded():
    for file in listdir(csvDownloadDir):
        if file[-4:] == ".csv":
            return True 
    return False


def getTheExistingCsvName():
    csv = listdir(csvDownloadDir)[0]
    
    return csv


def deleteCsvFile():
    remove(file)

def validStudentNumber(potentialNum):
    if len(potentialNum) != 9:
        return False

    return True


def compareEmailWithInput(email, inputNumber):
    #retrieve student number from email
    try:
        csvNumber = email[:email.index('@')]
    except: #will except if email doesnt contain an @
        return False

    if not validStudentNumber(csvNumber):
        return False

    if csvNumber == inputNumber:
        return True
    else:
        return False


def searchCsv(csvPath, studentNoInput):
    with open(csvPath) as memberCsv:
        csvReader = csv.reader(memberCsv, delimiter=',')

        next(csvReader, None)  # skip the headers

        for row in csvReader:
            if (compareEmailWithInput(row[2], studentNoInput)):
                return True
        
        return False

def hasAlreadyBeenUsed(studentNoInput):
    f = open("previouslyVerifiedNumbers.json")
    data = json.load(f)
    f.close()

    for number in data["numberList"]:
        number = number.lower()
        if(number == studentNoInput):
            return True

    return False
    

def addNumberToVerifiedJson(studentNoInput):
    f = open("previouslyVerifiedNumbers.json", "r")
    data = json.load(f)
    f.close()
    
    data["numberList"].append(studentNoInput)

    jsonObject = json.dumps(data, indent = 4)

    f = open("previouslyVerifiedNumbers.json", "w")
    f.write(jsonObject)
    f.close()



def isRegistered(studentNoInput):
    
    if not validStudentNumber(studentNoInput):
        print("Invalid input")
        return False

    studentNoInput = studentNoInput.lower()

    if hasAlreadyBeenUsed(studentNoInput):
        print("Has already been used")
        return False

    if downloadCsv():
        csv = getTheExistingCsvName()

        print(csv)

        if searchCsv(csv, studentNoInput):
            print("Student is Registered!")
            

            addNumberToVerifiedJson(studentNoInput)
            deleteCsvFile(csv)
            return True
        else:
            print("Student is not Registered")
            deleteCsvFile(csv)
            return False

#print(searchCsv("membershipExport_2022-04-10.csv", "c20375736"))
#"membershipExport_2022-04-10.csv"

    
