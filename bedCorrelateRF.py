'''
Search: https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4
Using all the 13 search results
Created directory "filesBed" and directory "gz" under "filesBed" directory
Downloaded 13 .bed.gz files into "gz" directory that were of output type "replicate peaks" and of isogenic type "1,2"
Unzipped 13 .bed.gz files into 13 .bed files in "filesBed" directory
'''

import time

# starting time
start_time = time.time()

from pybedtools import BedTool
from multiprocessing import Pool
import glob
import subprocess
import sys

bedPairedVariables = dict()
bedPairedVariablesList = []
bedToolsVariables = dict()

def jaccardBed():
    bedList = []
    pairingList = []
    pairList = []

    # finding all bed files in "filesBed" directory
    for name in glob.glob('./filesBed/*.bed'):
        bedList.append(name)

    # creating new directory "filesSortedBed" where sorted bed files wil lgo
    bashCommand = 'mkdir filesSortedBed'
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    process.communicate()

    for name, index in zip(bedList, range(len(bedList))):
        original = sys.stdout
        splitName = name.split('/')
        bedName = './filesSortedBed/' + splitName[2]
        sys.stdout = open(bedName, 'w')
        # sorting bed files
        bashCommand = 'sort -k1,1 -k2,2n ' + bedList[index]
        process = subprocess.Popen(bashCommand.split(), stdout=sys.stdout)
        process.communicate()
        # redirecting stdout back to console
        sys.stdout = original
        bedToolsName = splitName[2].split('.')[0]
        bedFilesName = bedName
        # creating a dictionary of variables creating bed tools with the sorted bed files
        bedToolsVariables[bedToolsName] = BedTool(bedFilesName)

    for name in bedToolsVariables:
        pairingList.append(name)

    '''
    for name in bedToolsVariables:
        pairingList.append(bedToolsVariables[name])
    '''

    # generating unique pairs of bed files to correlate
    def pairCall():

        def pair(arrayPair):
            for i in range(len(arrayPair) - 1):
                interPair = [arrayPair[0], arrayPair[i]]
                pairList.append(interPair)
                if i == len(arrayPair) - 2:
                    interPair = [arrayPair[0], arrayPair[i + 1]]
                    pairList.append(interPair)
                    arrayPair.pop(0)
                    pair(arrayPair)
                if len(arrayPair) == 1:
                    interPair = [arrayPair[0], arrayPair[0]]
                    pairList.append(interPair)
                    arrayPair.pop(0)

        pair(pairingList)

    pairCall()

    global bedPairedVariables

    for pair, index in zip(pairList, range(len(pairList))):
        bedPairedVariables[index] = pair

    # print(bedPairedVariables)
    print(bedToolsVariables)

def callJaccardBed(bedPairs):
    try:
        # print("ALERT")
        # print(bedPairs[0])
        bedPairsTrial = exec(bedPairs[0])
        jaccardResults = BedTool.jaccard(bedPairsTrial)
        print(jaccardResults["jaccard"])
        '''
        for pair in bedPairs:
            jaccardResults = BedTool.jaccard(exec(*bedPairs[pair]))
            print(jaccardResults["jaccard"])
        '''
    except Exception as error:
        print("error")
        print(error)
    '''
    for key, value in bedPairs.items():
        # print(key)
        # print(value)
        jaccardResults = BedTool.jaccard(exec(value[0]))
        # print(jaccardResults)
        print(jaccardResults["jaccard"])
    '''
    '''
    for index in range(len(bedPairedVariables)):
        bedPairedVariablesList.append(bedPairedVariables[index])

    for key, value in bedPairs.items():
        jaccardResults = BedTool.jaccard(*value)
        print(jaccardResults)
        print(jaccardResults["jaccard"])
    '''

def main():
    jaccardBed()
    global bedPairedVariables
    # print(bedPairedVariables)
    callJaccardBed(bedPairedVariables)

    '''
    print(bedPairedVariables)
    numProcs = len(bedPairedVariables)
    for index in bedPairedVariables:
        bedPairedVariables[str(index)] = bedPairedVariables.pop(index)

    with Pool(numProcs) as p:
        p.map(callJaccardBed, bedPairedVariables)
        # p.map(callJaccardBed(**bedPairedVariables))
        # for index in bedPairedVariables:
            # p.map(callJaccardBed, bedPairedVariables)
    '''

main()

# printing time (after subtracting ending time - starting time) to two decimal places
print('--- %.2f seconds ---' % (time.time() - start_time))


