# chipseq

This program calculates jaccard correlations between replicated peaks bed files from general histone ENCODE search queries.
You may execute this program in the command line in your conda environment once all the necessary packages are installed.

Example (to correlate URL: https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4):

python bedCorrelateGeneral.py 'https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4&format=json'

JSON of search results downloaded and parsed to get ENCSRs
ENCSRs jsons downloaded and parsed with these criteria (file type: bed narrowPeak, output type: replicated peaks, assembly: GRCh38) to get ENCFFs
Bed files downloaded, unzipped, and correlated to get jaccard scores
