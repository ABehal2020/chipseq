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
from itertools import combinations_with_replacement
import glob
import subprocess
import sys

def jaccardBed():
    bedList = []
    sortedBedList = []

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
        sortedBedList.append( bedName )
        # redirecting stdout back to console
        sys.stdout = original

    # generating unique pairs of bed files to correlate
    bedSortedPairs = list(combinations_with_replacement(sortedBedList, 2))

    return bedSortedPairs

# not multi-threaded
def sequentialJaccardBed():
    bedSortedPairs = jaccardBed()
    jaccardScores = []
    errorBedSortedPairs = []

    for pair in bedSortedPairs:
        try:
            file1 = BedTool(pair[0])
            file2 = BedTool(pair[1])
            jaccardResults = BedTool.jaccard(file1, file2)
            jaccardScores.append(jaccardResults["jaccard"])
        except Exception as error:
            errorBedSortedPair = [file1, file2]
            errorBedSortedPairs.append(errorBedSortedPair)
            # print("error")
            # print(error)

    print(jaccardScores)
    print(errorBedSortedPairs)

# multi-threaded
def multithreadedJaccardBed(*bedSortedPairs):
    # bedSortedPairs = jaccardBed()
    jaccardScores = []
    errorBedSortedPairs = []
    try:
        file1 = BedTool(bedSortedPairs[0][0])
        file2 = BedTool(bedSortedPairs[0][1])
        jaccardResults = BedTool.jaccard(file1, file2)
        jaccardScore = jaccardResults["jaccard"]
        jaccardScores.append(jaccardScore)
    except Exception as error:
        errorBedSortedPair = [file1, file2]
        errorBedSortedPairs.append(errorBedSortedPair)

    print(jaccardScores)
    print(errorBedSortedPairs)

    return jaccardScores, errorBedSortedPairs

# calling multi-threaded jaccard calculation function
def fetchScoreAndErrors():
    # multi-threaded call
    bedSortedPairs = jaccardBed()
    numProcs = len(bedSortedPairs)
    with Pool(numProcs) as p:
        p.map(multithreadedJaccardBed, bedSortedPairs)

def main():
    # not multi-threaded call
    # sequentialJaccardBed()
    # multi-threaded call
    fetchScoreAndErrors()

main()

# printing time (after subtracting ending time - starting time) to two decimal places
print('--- %.2f seconds ---' % (time.time() - start_time))


