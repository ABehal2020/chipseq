'''
This program calculates jaccard correlations between replicated peaks bed files from general histone ENCODE search queries.
You may execute this program in the command line in your conda environment once all the necessary packages are installed.
Example (to correlate URL: https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4):
python pyranges_jaccard.py 'https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4&format=json'
JSON of search results downloaded and parsed to get ENCSRs
ENCSRs jsons downloaded and parsed with these criteria (file type: bed narrowPeak, output type: replicated peaks, assembly: GRCh38) to get ENCFFs
Bed files downloaded, unzipped, and correlated to get jaccard scores
'''

import time

# starting time
start_time = time.time()

import glob
import sys
import pyranges as pr
from multiprocessing import Pool
from itertools import combinations_with_replacement
from json_parse import sequential_encsr_encff, fetch_encsr_encff

def jaccardBed():
    pair_time = time.time()
    bed_paths = []

    # finding all bed files in "filesBed" directory
    for name in glob.glob('./bedAuto/filesBed/*.bed'):
        bed_paths.append(name)

    # generating unique pairs of bed files to correlate
    bed_pairs = list(combinations_with_replacement(bed_paths, 2))

    print('Pairing bed files --- %.2f seconds ---' % (time.time() - pair_time))

    return bed_pairs

# not multi-threaded
def sequentialJaccardBed():
    sequential_time = time.time()
    bed_pairs = jaccardBed()
    jaccard_scores = []
    error_bed_pairs = []

    for pair in bed_pairs:
        try:
            file1 = pr.read_bed(pair[0])
            file2 = pr.read_bed(pair[1])
            jaccard_score = file1.stats.jaccard(file2)
            jaccard_scores.append(jaccard_score)
        except Exception as error:
            print('error')
            print(error)
            error_bed_pair = [file1, file2]
            error_bed_pairs.append(error_bed_pair)

    print('scores')
    print(jaccard_scores)
    print('errors')
    print(error_bed_pairs)

    print('Sequentially calculating jaccard scores --- %.2f seconds ---' % (time.time() - sequential_time))

# multi-threaded
def multithreadedJaccardBed(*bed_pairs):
    # bedSortedPairs = jaccardBed()
    jaccard_scores = dict()
    error_bed_pairs = []
    try:
        file1 = pr.read_bed(bed_pairs[0][0])
        file2 = pr.read_bed(bed_pairs[0][1])
        jaccard_score = file1.stats.jaccard(file2)
        scored_pair = (bed_pairs[0][0], bed_pairs[0][1])
        jaccard_scores[str(scored_pair)] = jaccard_score
    except Exception as error:
        print('error')
        print(error)
        error_bed_pair = [file1, file2]
        error_bed_pairs.append(error_bed_pair)

    return jaccard_scores, error_bed_pairs

# calling multi-threaded jaccard calculation function
def fetch_scores_and_errors():
    fetch_multithreaded_time = time.time()
    jaccard_scores = dict()
    error_bed_pairs = []
    bed_pairs = jaccardBed()
    num_processes = 2*len(bed_pairs)

    with Pool(num_processes) as p:
        scores_and_errors = p.map(multithreadedJaccardBed, bed_pairs)

    for score, error in scores_and_errors:
        jaccard_scores.update(score)
        if len(error) != 0:
            error_bed_pairs.append(error)

    print('scores')
    print(jaccard_scores)
    print('errors')
    print(error_bed_pairs)

    print('Fetching multithreaded calculations results (jaccard scores and errors) --- %.2f seconds ---' % (time.time() - fetch_multithreaded_time))


def main(args):
    # not multi-threaded
    # sequential_encsr_encff(args)
    # multi-threaded
    fetch_encsr_encff(args)
    # not multi-threaded call - around 200 seconds in total for the whole program to execute
    # sequentialJaccardBed()
    # multi-threaded call - around 40 seconds in total for the whole program to execute
    fetch_scores_and_errors()
    # printing time (after subtracting ending time - starting time) to two decimal places
    print('Total time --- %.2f seconds ---' % (time.time() - start_time))

if __name__ == '__main__':
    main(sys.argv[1:])