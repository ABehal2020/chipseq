'''
This program calculates jaccard correlations between replicated peaks bed files from general histone ENCODE search queries.
You may execute this program in the command line in your conda environment once all the necessary packages are installed.
Example (to correlate URL: https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4):
python bedBash.py 'https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4&format=json'
JSON of search results downloaded and parsed to get ENCSRs
ENCSRs jsons downloaded and parsed with these criteria (file type: bed narrowPeak, output type: replicated peaks, assembly: GRCh38) to get ENCFFs
Bed files downloaded, unzipped, and correlated to get jaccard scores
'''

import time
import glob
import subprocess
import sys
import os
from pybedtools import BedTool
from multiprocessing import Pool
from itertools import combinations_with_replacement
from jsonParse import encsr_encff, start_time

def jaccardBed():
    sort_pair_time = time.time()
    bedList = []
    sortedBedList = []

    # finding all bed files in "filesBed" directory
    for name in glob.glob('./bedAuto/filesBed/*.bed'):
        bedList.append(name)

    # print(bedList)
    bedList.remove('./bedAuto/filesBed/ENCFF141BCE.bed')
    bedList.remove('./bedAuto/filesBed/ENCFF764NQG.bed')
    bedList.remove('./bedAuto/filesBed/ENCFF384IAN.bed')

    # creating new directory "filesSortedBed" where sorted bed files wil lgo
    bashCommand = 'mkdir -p ./bedAuto/filesSortedBed'
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    process.communicate()

    for name, index in zip(bedList, range(len(bedList))):
        original = sys.stdout
        splitName = name.split('/')
        bedName = './bedAuto/filesSortedBed/' + splitName[3]
        sys.stdout = open(bedName, 'w')
        # sorting bed files
        bashCommand = 'sort -k1,1 -k2,2n ' + bedList[index]
        process = subprocess.Popen(bashCommand.split(), stdout=sys.stdout)
        process.communicate()
        sortedBedList.append(bedName)
        # redirecting stdout back to console
        sys.stdout = original

    # generating unique pairs of bed files to correlate
    bedSortedPairs = list(combinations_with_replacement(sortedBedList, 2))

    print('Sorting bed files and pairing them --- %.2f seconds ---' % (time.time() - sort_pair_time))

    return bedSortedPairs

# not multi-threaded
def sequentialJaccardBed():
    sequential_time = time.time()
    bedSortedPairs = jaccardBed()
    jaccardScores = []
    errorBedSortedPairs = []
    bashCommands = []

    for pair in bedSortedPairs:
        try:
            file1 = BedTool(pair[0])
            file2 = BedTool(pair[1])
            # jaccardResults = BedTool.jaccard(file1, file2)
            # jaccardScores.append(jaccardResults['jaccard'])
            bashCommand = 'bedtools jaccard -a ' + pair[0] + ' -b ' + pair[1]
            bashCommands.append(bashCommand)
            '''
            process = subprocess.Popen( bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            o, e = process.communicate()
            # time.sleep(.500)
            print('-------------------------------')
            print(bashCommand)
            print('f1: ' + str(pair[0]))
            print('f2: ' + str(pair[1]))
            print('Output: ' + o.decode( 'ascii' ))
            print('Error: ' + e.decode( 'ascii' ))
            print('code: ' + str( process.returncode ))
            print('-------------------------------')
            '''
        except Exception as error:
            print('error oh no bash commands list not finished')
            errorBedSortedPair = [file1, file2]
            errorBedSortedPairs.append(errorBedSortedPair)
            # print('error')
            # print(error)
    '''
    print('*****')
    print(bashCommands)
    print('*****')
    '''

    for index in range(len(bashCommands)):
        # print(command)
        process = subprocess.Popen(bashCommands[index].split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        o, e = process.communicate()
        # time.sleep(.500)
        print('-------------------------------')
        print(bashCommands[index])
        print('f1: ' + str( pair[0] ))
        print('f2: ' + str( pair[1] ))
        print('Output: ' + o.decode( 'ascii' ))
        print('Error: ' + e.decode( 'ascii' ))
        print('code: ' + str( process.returncode ))
        print('-------------------------------')

    print('Sequentially calculating jaccard scores --- %.2f seconds ---' % (time.time() - sequential_time))

# multi-threaded
def multithreadedJaccardBed(*bedSortedPairs):
    # bedSortedPairs = jaccardBed()
    jaccardScores = dict()
    errorBedSortedPairs = []
    try:
        if (os.stat(bedSortedPairs[0][0]).st_size >= os.stat(bedSortedPairs[0][1]).st_size):
            print('true')
            file1 = BedTool(bedSortedPairs[0][0])
            file2 = BedTool(bedSortedPairs[0][1])
            # jaccardResults = BedTool.jaccard( file1, file2 )
            # jaccardScore = jaccardResults['jaccard']
            jaccardScore = 0
            scoredPair = (file1, file2)
            jaccardScores[str( scoredPair )] = jaccardScore

            bashCommand = 'bedtools jaccard -a ' + bedSortedPairs[0][0] + ' -b ' + bedSortedPairs[0][1]
            process = subprocess.Popen( bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            o, e = process.communicate()

            print('Output: ' + o.decode( 'ascii' ))
            # print('Error: ' + e.decode( 'ascii' ))
            # print('code: ' + str( process.returncode ))

        else:
            print('yuck')
            file1 = BedTool(bedSortedPairs[0][1])
            file2 = BedTool(bedSortedPairs[0][0])
            # jaccardResults = BedTool.jaccard( file1, file2 )
            # jaccardScore = jaccardResults['jaccard']
            jaccardScore = 0
            scoredPair = (file1, file2)
            jaccardScores[str( scoredPair )] = jaccardScore

            bashCommand = 'bedtools jaccard -a ' + bedSortedPairs[0][0] + ' -b ' + bedSortedPairs[0][1]
            process = subprocess.Popen( bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            o, e = process.communicate()

            print('Output: ' + o.decode( 'ascii' ))
            print('Error: ' + e.decode( 'ascii' ))
            print('code: ' + str( process.returncode ))
        '''
        jaccardResults = BedTool.jaccard(file1, file2)
        jaccardScore = jaccardResults['jaccard']
        scoredPair = (file1, file2)
        jaccardScores[str(scoredPair)] = jaccardScore
        '''
    except Exception as error:
        if (os.stat(bedSortedPairs[0][0]).st_size >= os.stat(bedSortedPairs[0][1]).st_size):
            print('ok!')
            print('***')
            print(bedSortedPairs[0][0])
            print(bedSortedPairs[0][1])
            print('***')
        else:
            print('youch!')
            print('-----')
            print(bedSortedPairs[0][0])
            print(bedSortedPairs[0][1])
            print('-----')
        errorBedSortedPair = [file1, file2]
        errorBedSortedPairs.append(errorBedSortedPair)
        print('error')
        print(error)

    return jaccardScores, errorBedSortedPairs

# calling multi-threaded jaccard calculation function
def fetchScoreAndErrors():
    fetch_multithreaded_time = time.time()
    # multi-threaded call
    jaccardScores = dict()
    errorBedSortedPairs = []
    bedSortedPairs = jaccardBed()
    # numProcs = len(bedSortedPairs)
    numProcs = 1

    with Pool(numProcs) as p:
        scoreAndErrors = p.map(multithreadedJaccardBed, bedSortedPairs)

    for score, error in scoreAndErrors:
        jaccardScores.update(score)
        if len(error) != 0:
            errorBedSortedPairs.append(error)

    print('scores')
    print(jaccardScores)
    print('errors')
    print(errorBedSortedPairs)

    print('Fetching multithreaded calculations results (jaccard scores and errors) --- %.2f seconds ---' % (time.time() - fetch_multithreaded_time))


def main(args):
    encsr_encff( args )
    # not multi-threaded call
    sequentialJaccardBed()
    # multi-threaded call
    # fetchScoreAndErrors()
    print('Total time --- %.2f seconds ---' % (time.time() - start_time))

# printing time (after subtracting ending time - starting time) to two decimal places

if __name__ == '__main__':
    main(sys.argv[1:])