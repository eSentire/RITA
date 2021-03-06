##########################################
#           INTERNAL LIBRARIES           #    
##########################################
from yay_its_a_loading_bar import progress_bar
import colors
from data import ESServer
from field_names import *
from module import Module

##########################################
#              MODULE SETUP              #    
##########################################
NAME = 'duration'
DESC = 'Look for Connections with Unusually Long Duration'

# Default percentage of longest durations to be retained
DURATION_THESHOLD = 0.02

OPTS = {
        "customer": {
            "value": "",
            "type": "string"
            },
        "threshold": {
            "value": DURATION_THESHOLD,
            "type": "number"
            },
        "result_type": {
            "value": 'long_durations',
            "type": "string"
            },
        "server": {
            "value": "http://localhost:9200",
            "type": "string"
            }
        }

class DurationModule(Module):
    def __init__(self):
        super(DurationModule, self).__init__(NAME, DESC, OPTS)

    def RunModule(self):
        run(self.options["customer"]["value"], 
            self.options["threshold"]["value"],
            self.options["result_type"]["value"],
            self.options["server"]["value"])

##########################################
#           END MODULE SETUP             #    
##########################################


def write_data(data, customer, result_type):
    # Iterate over each item 
    for item in data:
        # format new entry
        entry = {}
        entry[SOURCE_IP]        = item['fields'][SOURCE_IP]
        entry[SOURCE_PORT]      = item['fields'][SOURCE_PORT]
        entry[DESTINATION_IP]   = item['fields'][DESTINATION_IP]
        entry[DESTINATION_PORT] = item['fields'][DESTINATION_PORT]
        entry[DURATION]         = item['fields'][DURATION]
        entry[TIMESTAMP]        = item['fields'][TIMESTAMP]

        # write entry to elasticsearch
        ht_data.write_data(entry, customer, result_type)
        

def find_long_durations(customer, threshold, result_type):
    # searching for duration in log files, not results
    doc_type = 'logs'

    # fields to return from elasticsearch query
    fields = [SOURCE_IP, SOURCE_PORT,DESTINATION_IP,DESTINATION_PORT, DURATION, TIMESTAMP]
    
    # restrict results to specified customer
    constraints = []
    
    # anything we want to filter out
    ignore = []

    scroll_id = ""
    scroll_len = 1000

    scrolling = True

    print(colors.bcolors.OKBLUE + '>>> Retrieving information from elasticsearch...')

    # YE OLDE JSON QUERY
    sort = DURATION + ':desc'

    results = []

    __, _, scroll_size = ht_data.get_data(customer, doc_type,fields, constraints, ignore, scroll_id, scroll_len, sort)

    # determine percentage of results to be kept
    num_needed = int(scroll_size * threshold)
    num_remaining = num_needed

    # Get elasticsearch results sorted by duration time, and keep top percentage as set by THRESHOLD
    while scrolling:
        # Retrieve data
        hits, scroll_id, scroll_size = ht_data.get_data(customer, doc_type,fields, constraints, ignore, scroll_id, scroll_len, sort)

        results += hits

        num_remaining -= len(hits)

        if len(hits) < 1 or num_remaining <= 0:
            scrolling = False
            results = results[0:num_needed]

    num_found = len(results)

    print(colors.bcolors.WARNING + '[!] ' + str(num_found) + ' results found! [!]'+ colors.bcolors.ENDC)

    if (num_found > 0):
        print(colors.bcolors.OKBLUE + '>>> Writing results of analysis...')
        write_data(results, customer, result_type)
        print('>>> ... Done!' + colors.bcolors.ENDC)
    else:
        print ('Verify \'duration\' field exists in your log configuration file!'+ colors.bcolors.ENDC)
        

def run(customer, threshold, result_type, server="http://localhost:5000/"):
    global ht_data
    ht_data = ESServer(server)

    print(colors.bcolors.OKBLUE + '[-] Finding long connections for customer ' 
          + colors.bcolors.HEADER + customer 
          + colors.bcolors.OKBLUE + ' [-]'
          + colors.bcolors.ENDC)

    # Delete Previous Results
    ht_data.delete_results(customer, result_type)
    
    find_long_durations(customer, threshold, result_type)

    print(colors.bcolors.OKGREEN + '[+] Finished checking long connections for customer ' 
          + colors.bcolors.HEADER + customer 
          + colors.bcolors.OKGREEN + ' [+]'
          + colors.bcolors.ENDC)

