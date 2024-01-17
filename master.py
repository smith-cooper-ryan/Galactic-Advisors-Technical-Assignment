import re
import os
import textract
import pathlib
from pathlib import Path
import pandas as pd
import numpy as np
import zipfile
import shutil

def ssnSearch(text, outFile):
    search  = r'(?!(\d){3}(-| |)\1{2}\2\1{4})(?!666|000|9\d{2})(\b\d{3}(-| |)(?!00)\d{2}\4(?!0{4})\d{4}\b)'
    results = re.findall(search, text)
    for result in results:
        result = result[2]
        result = str(result)
        result = result.replace(' ','')
        result = result.replace('-','')
        result = result.replace('.','')
        outFile.write("SSN: " + result + '\n')
        
def luhn(ccn):
    def digitsOf(n):
        return [int(d) for d in str(n)]
    digits = digitsOf(ccn)
    odd = digits[-1::-2]
    even = digits[-2::-2]
    checksum = 0
    checksum += sum(odd)
    for d in even:
        checksum += sum(digitsOf(d*2))
    checksum %= 10
    if checksum == 0:
        return True
    else:
        return False
        
def ccnSearch(text, outFile):
    search = r'\b(?:\d[ -]*?){13,16}\b'
    results = re.findall(search, text)
    for result in results:
        result = str(result)
        result = result.replace(' ','')
        result = result.replace('-','')
        result = result.replace('.','')
        if luhn(result) == True:
            outFile.write("CCN: " + result + '\n')
        else:
            pass
            
excel = ('.xlsx', '.ods')

def excelHandler(text):
    text = pd.read_excel(text)
    text.to_numpy().tolist()
    return text
  
compressed = ('.zip', '.gz')

def zipHandler(text, driveName):
    if str(text).endswith('.zip'):
        with zipfile.ZipFile(text,"r") as zip_ref:
            zip_ref.extractall(driveName)
    elif str(text).endswith('.gz'):
        shutil.unpack_archive(filename=text, extract_dir=driveName)
        
def driveSearch(driveName):
    out = open('report.txt', 'w')
    drive = pathlib.Path(driveName)
    for item in drive.rglob("*"):
        if item.is_file():
            if str(item).endswith(excel):
                text = excelHandler(item)
                text = str(text)
                ssnSearch(text, out)
                ccnSearch(text, out)
            elif str(item).endswith(compressed):
                zipHandler(item, driveName)
            else:
                try:
                    text = textract.process(item)
                    text = text.decode('ascii')
                    text = str(text)
                    ssnSearch(text, out)
                    ccnSearch(text, out)
                except:
                    print("ERROR. File: " + str(item) + " is unreadable.")
                    pass
    out.close()        
    
if __name__ == "__main__":
    print("Welcome! This program scans a given drive or directory for Credit Card (CCNs) and Social Security Numbers (SSNs).")
    print("When this program has completed, a report will be generated containing those numbers. You can find that report in the directory where you run this program from.")
    driveName = input("Please input the address of the drive to be scanned: ")
    driveSearch(driveName)
