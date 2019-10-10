'''
Search: https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4
Using all the search results except for third and fourth results
Downloaded .bed.gz files that were of output type "replicate peaks" and of isogenic type "1,2" into folder "gz" (created in same directory as this program)
'''

import time

# starting time
start_time = time.time()

from pybedtools import BedTool
from multiprocessing import Pool

# making BedTools for bed files
# also sorting bed files lexicographically (dictionary order) prior to using jaccard method
# note: not necessary to unzip gz file
a = BedTool('./bedFiles/gz/ENCFF017NXL.bed.gz').sort()
b = BedTool('./bedFiles/gz/ENCFF125JFQ.bed.gz').sort()
c = BedTool('./bedFiles/gz/ENCFF903QKE.bed.gz').sort()
d = BedTool('./bedFiles/gz/ENCFF106NXV.bed.gz').sort()
e = BedTool('./bedFiles/gz/ENCFF071XMA.bed.gz').sort()
f = BedTool('./bedFiles/gz/ENCFF764NQG.bed.gz').sort()
g = BedTool('./bedFiles/gz/ENCFF384IAN.bed.gz').sort()
h = BedTool('./bedFiles/gz/ENCFF155USN.bed.gz').sort()
i = BedTool('./bedFiles/gz/ENCFF137YUF.bed.gz').sort()
j = BedTool('./bedFiles/gz/ENCFF871JIL.bed.gz').sort()
k = BedTool('./bedFiles/gz/ENCFF460EIG.bed.gz').sort()

'''
# Pairing algorithm - will incorporate it into the workflow in the future

array = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]

def pairCall():
    pairList = []

    def pair(arrayPair):
        for i in range(len(arrayPair)-1):
            interPair = [arrayPair[0], arrayPair[i]]
            pairList.append(interPair)
            if i == len(arrayPair) - 2:
                interPair = [arrayPair[0], arrayPair[i+1]]
                pairList.append(interPair)
                arrayPair.pop(0)
                pair(arrayPair)
            if len(arrayPair) == 1:
                interPair = [arrayPair[0], arrayPair[0]]
                pairList.append(interPair)
                arrayPair.pop(0)

    pair(array)
    print(pairList)
'''

# Obviously, there's a better way to do this (will improve it soon)
bedList1 = [a, a]
bedList2 = [a, b]
bedList3 = [a, c]
bedList4 = [a, d]
bedList5 = [a, e]
bedList6 = [a, f]
bedList7 = [a, g]
bedList8 = [a, h]
bedList9 = [a, i]
bedList10 = [a, j]
bedList11 = [a, k]

bedList12 = [b, b]
bedList13 = [b, c]
bedList14 = [b, d]
bedList15 = [b, e]
bedList16 = [b, f]
bedList17 = [b, g]
bedList18 = [b, h]
bedList19 = [b, i]
bedList20 = [b, j]
bedList21 = [b, k]

bedList22 = [c, c]
bedList23 = [c, d]
bedList24 = [c, e]
bedList25 = [c, f]
bedList26 = [c, g]
bedList27 = [c, h]
bedList28 = [c, i]
bedList29 = [c, j]
bedList30 = [c, k]

bedList31 = [d, d]
bedList32 = [d, e]
bedList33 = [d, f]
bedList34 = [d, g]
bedList35 = [d, h]
bedList36 = [d, i]
bedList37 = [d, j]
bedList38 = [d, k]

bedList39 = [e, e]
bedList40 = [e, f]
bedList41 = [e, g]
bedList42 = [e, h]
bedList43 = [e, i]
bedList44 = [e, j]
bedList45 = [e, k]

bedList46 = [f, f]
bedList47 = [f, g]
bedList48 = [f, h]
bedList49 = [f, i]
bedList50 = [f, j]
bedList51 = [f, k]

bedList52 = [g, g]
bedList53 = [g, h]
bedList54 = [g, i]
bedList55 = [g, j]
bedList56 = [g, k]

bedList57 = [h, h]
bedList58 = [h, i]
bedList59 = [h, j]
bedList60 = [h, k]

bedList61 = [i, i]
bedList62 = [i, j]
bedList63 = [i, k]

bedList64 = [j, j]
bedList65 = [j, k]

bedList66 = [k, k]

bedList = [bedList1, bedList2, bedList3, bedList4, bedList5, bedList6, bedList7, bedList8, bedList9, bedList10, bedList11, bedList12, bedList13, bedList14, bedList15, bedList16, bedList17, bedList18, bedList19, bedList20, bedList21, bedList22, bedList23, bedList24, bedList25, bedList26, bedList27, bedList28, bedList29, bedList30, bedList31, bedList32, bedList33, bedList34, bedList35, bedList36, bedList37, bedList38, bedList39, bedList40, bedList41, bedList42, bedList43, bedList44, bedList45, bedList46, bedList47, bedList48, bedList49, bedList50, bedList51, bedList52, bedList53, bedList54, bedList55, bedList56, bedList57, bedList58, bedList59, bedList60, bedList61, bedList62, bedList63, bedList64, bedList65, bedList66]

# bedFiles should be list that is exactly length of 2
def calcJaccard(bedFiles):
    # jaccard method returns dictionary
    try:
        BedTool.jaccard(*bedFiles)
        # jaccardResults = BedTool.jaccard(*bedFiles)
        # print(jaccardResults)
        # print(jaccardResults["jaccard"]
    # for some jaccard calculations, getting this error: "ValueError: not enough values to unpack (expected 2, got 0)"
    except:
        pass
        # print("error")

# Method 1: not parallelized - around 6.5 seconds
'''
for i in range(len(bedList)):
    calcJaccard(bedList[0])
'''

def main(args):
    for i in range(len(bedList)):
        print(calcJaccard(bed))

if __name__ == '__main__':
    # method 2: parallelize - around 3.0 seconds
    numProcs = len(bedList)
    with Pool(numProcs) as p:
        p.map(calcJaccard, bedList)
        # print(p.map(calcJaccard, bedList))

# printing time (after subtracting ending time - starting time) to two decimal places
print("--- %.2f seconds ---" % (time.time() - start_time))

