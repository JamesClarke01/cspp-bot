import os
from os import listdir, remove

import json

import csv

from decouple import config  #for reading env files

from selenium import webdriver
from selenium.webdriver.common.by import By


#global constants start
CSV_PAGE = "https://www.tudublin.ie/socsportal/admin/index.php?object=T3JnYW5pc2F0aW9uTWVtYmVy&organisationID=MTA2NQ==&actionType=cmVhZA==&action=Ng==&method=Y3N2RXhwb3J0"

PAST_NUMBER_JSON = "previouslyVerifiedNumbers.json"

CSV_DOWNLOAD_DIR = os.getcwd()

USER = config('U')
P = config('P')


#global constants end

def setupChromeDriver():
    #selenium setup
    chromeOptions = webdriver.ChromeOptions()

    prefs = {"download.default_directory" : CSV_DOWNLOAD_DIR}

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
    """Will run function passed a defined amount of time until the function returns something or the limit is succeeded"""
    cycleWaitTime = 100000
    
    for i in range(cycleWaitTime):
        funcReturnValue = funcThatRequiresLoaded(*args)
        
        if funcReturnValue != None:
            print(funcThatRequiresLoaded, "successful")
            return funcReturnValue

        elif i == cycleWaitTime-1:
            print(funcThatRequiresLoaded, "unsuccessful")
            return None

    
def downloadCsv():

    driver = setupChromeDriver()
    
    driver.get(CSV_PAGE) #open page
    
    #bypass page 1
    if waitUntilLoaded(bypassPage1, driver) == None:
        return False

    #bypass page 2
    if waitUntilLoaded(bypassPage2, driver) == None:
        return False
    
    #download csv
    csvName = waitUntilLoaded(csvDownloadedChecker)
    if csvName == None:
        return False

    return csvName

def csvDownloadedChecker():
    for file in listdir(CSV_DOWNLOAD_DIR):
        if file[-4:] == ".csv":
            return file 
    return None

def deleteCsvFile(file):
    "Function as an extra check because remove() is scary"
    if file[-4:] == ".csv":
        remove(file)

def validStudentNumber(potentialNum):
    "Input validation for the student number entry"
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

def searchCsv(memberCsv, studentNoInput):
    "Return True if number found, False if not"
    with open(memberCsv) as memberCsv:
        csvReader = csv.reader(memberCsv, delimiter=',')

        next(csvReader, None)  # skip the headers

        for row in csvReader:
            if (compareEmailWithInput(row[2], studentNoInput)):
                return True
        
        return False

def unusedPreviously(studentNoInput):
    f = open(PAST_NUMBER_JSON)
    data = json.load(f)
    f.close()

    for number in data["numberList"]:
        number = number.lower()
        if(number == studentNoInput):
            return False

    return True

def addNumberToVerifiedJson(studentNoInput):
    f = open(PAST_NUMBER_JSON, "r")
    data = json.load(f)
    f.close()
    
    data["numberList"].append(studentNoInput)

    jsonObject = json.dumps(data, indent = 4)

    f = open("previouslyVerifiedNumbers.json", "w")
    f.write(jsonObject)
    f.close()

    print("Number added to json")

def registeredOnPortal(studentNoInput):

    #make sure the csv directory is clear of old csvs before proceeding
    while(csvDownloadedChecker() != None):
        file = csvDownloadedChecker()
        deleteCsvFile(file)
    
    memberCsv = downloadCsv()  #download csv
    
    returnBool = searchCsv(memberCsv, studentNoInput)  #will be a true of false value

    deleteCsvFile(memberCsv)

    return returnBool

def isRegistered(studentNoInput):
    
    studentNoInput = studentNoInput.lower()  #make the input lowercase

    #first check if the input is 9 characters long, etc.
    if not validStudentNumber(studentNoInput):
        print("Invalid input")
        return False

    #check through the json of previously entered student numbers to make sure it hasn't already been entered
    if not unusedPreviously(studentNoInput):
        print("Has already been used")
        return False

    #check the student is registered on the portal
    if not registeredOnPortal(studentNoInput):
        print("Not registered on portal")
        return False

    #if here, student is defintely registered
    print("Student is registered")
    
    addNumberToVerifiedJson(studentNoInput)  #update json with new student number

    return True
