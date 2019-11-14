import time
import requests
import sys
import subprocess
import json
from sh import gunzip
from multiprocessing import Pool

def parseSearch(url):
    download_time = time.time()
    # url = 'https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4&format=json'
    encsrLinkList = []
    encsrNameList = []

    # making directories where bed files will be downloaded and unzipped
    bashCommand = 'mkdir -p ./bedAuto/jsonENCSR'
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    process.communicate()

    bashCommand = 'mkdir -p ./bedAuto/filesBed'
    process = subprocess.Popen( bashCommand.split(), stdout=subprocess.PIPE )
    process.communicate()

    # download json file of user search results
    filePath = './bedAuto/userSearch.json'
    r = requests.get(url, allow_redirects=True)

    with open(filePath, 'wb') as f:
        f.write(r.content)

    print('download search json --- %.2f seconds ---' % (time.time() - download_time))

    encsr_time = time.time()

    with open(filePath, 'r') as f:
        userSearch = json.load(f)

    userSearchFiltered = userSearch['@graph']

    # getting encsrs from json of user search results
    for element in range(len(userSearchFiltered)):
        if userSearchFiltered[element]['@id'][1:18] == 'experiments/ENCSR':
            encsrName = userSearchFiltered[element]['@id'][13:24]
            encsrNameList.append(encsrName)
            encsrLink = 'https://www.encodeproject.org/experiments/' + encsrName + '/?format=json'
            encsrLinkList.append(encsrLink)

    print('parse for encsr --- %.2f seconds ---' % (time.time() - encsr_time))

    return encsrNameList, encsrLinkList

# not multi-threaded
def sequential_encsr_encff(args):
    encff_time = time.time()
    filePath = './bedAuto/jsonENCSR/'
    encsrDict = dict()
    encffNames = []
    encffLinks = []

    encsrNameList, encsrLinkList = parseSearch(args[0])

    # getting encffs from jsons of encsrs
    # only encffs matching below criteria will be extracted from jsons of encsrs
    # file type: bed narrowPeak, output type: replicated peaks, assembly: GRCh38
    for encsrName, encsrLink in zip(encsrNameList, encsrLinkList):
        r = requests.get(encsrLink, allow_redirects=True)
        filePathCurrent = filePath + encsrName + '.json'
        with open(filePathCurrent, 'wb') as f:
            f.write(r.content)
        with open(filePathCurrent, 'r') as f:
            encsrDict[encsrName] = json.load(f)
        infoFiltered = encsrDict[encsrName]['files']
        for element in range(len(infoFiltered)):
            if infoFiltered[element]['file_type'] == 'bed narrowPeak' and infoFiltered[element]['output_type'] == 'replicated peaks':
                if infoFiltered[element]['assembly'] == 'GRCh38':
                    encffNames.append(infoFiltered[element]['cloud_metadata']['url'][-18:])
                    encffLinks.append(infoFiltered[element]['cloud_metadata']['url'])

    print('parse for encff --- %.2f seconds ---' % (time.time() - encff_time))

    download_time = time.time()
    encffPath = './bedAuto/filesBed/'

    # downloading and unzipping bed files
    for name, link in zip(encffNames, encffLinks):
        r = requests.get(link, allow_redirects=True)
        encffPathCurrent = encffPath + name
        with open(encffPathCurrent, 'wb') as f:
            f.write(r.content)
        gunzip(encffPathCurrent)

    print('download and unzip bed files --- %.2f seconds ---' % (time.time() - encff_time))

# multi-threaded
def multi_encsr_encff(*file_path):
    encsr_dict = dict()
    encff_names = []
    encff_links = []

    file_path = str(file_path)[2:-3]

    # getting encffs from jsons of encsrs
    # only encffs matching below criteria will be extracted from jsons of encsrs
    # file type: bed narrowPeak, output type: replicated peaks, assembly: GRCh38
    # for encsrName, encsrLink in zip(encsrNameList, encsrLinkList):
    with open(str(file_path), 'r') as f:
        encsr_dict[file_path] = json.load(f)

    info_filtered = encsr_dict[file_path]['files']

    for element in range(len(info_filtered)):
        if info_filtered[element]['file_type'] == 'bed narrowPeak' and info_filtered[element]['output_type'] == 'replicated peaks':
            if info_filtered[element]['assembly'] == 'GRCh38':
                encff_names.append(info_filtered[element]['cloud_metadata']['url'][-18:])
                encff_links.append(info_filtered[element]['cloud_metadata']['url'])

    return encff_names, encff_links

# calling multi-threaded encsr_encff parse function
def fetch_encsr_encff(args):
    fetch_encsr_time = time.time()
    file_path = './bedAuto/jsonENCSR/'
    file_path_all = []
    encff_names = []
    encff_links = []
    encsr_names, encsr_links = parseSearch(args[0])

    for encsr_name, encsr_link in zip(encsr_names, encsr_links):
        r = requests.get(encsr_link, allow_redirects=True)
        file_path_current = file_path + encsr_name + '.json'
        file_path_all.append(file_path_current)
        with open(file_path_current, 'wb') as f:
            f.write(r.content)

    num_processes = len(file_path_all)

    with Pool(num_processes) as p:
        encff_names_links = p.map(multi_encsr_encff, file_path_all)

    print('parse for encff --- %.2f seconds ---' % (time.time() - fetch_encsr_time))

    download_time = time.time()
    encff_path = './bedAuto/filesBed/'

    for encff_name, encff_link in encff_names_links:
        encff_names.append(str(encff_name)[2:-2])
        encff_links.append(str(encff_link)[2:-2])

    # downloading and unzipping bed files
    for name, link in zip(encff_names, encff_links):
        r = requests.get(link, allow_redirects=True)
        encff_path_current = encff_path + name
        with open(encff_path_current, 'wb') as f:
            f.write(r.content)
        gunzip(encff_path_current)

    print('download and unzip bed files --- %.2f seconds ---' % (time.time() - download_time))

def main(args):
    sequential_encsr_encff(args)

if __name__ == '__main__':
    main(sys.argv[1:])