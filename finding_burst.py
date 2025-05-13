# numerical essentials 
import numpy as np
import pandas as pd

# for plotting
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates

# for cdf reading
from spacepy import toolbox
#spacepy.toolbox.update(leapsecs=True)
from spacepy import pycdf

# other numerical tools
import os
import glob
from datetime import datetime,date,timedelta

# my own misc. functions
import sys
import find_ds as ds
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/data/emfisis_burst/wip/rablack75/rablack75/CreateBurst')


''' script to make a list of all the burst files that contain the related survey '''

start_date = date(year=2018, month=4, day=20)

# burst folder location 

wfr_folder ='/data/spacecast/wave_database_v2/RBSP-A/L2'
burst6 = 'rbsp-a_WFR-waveform-continuous-burst_emfisis-L2_'

burst_times = []

try:

    # String version of dates for filename  
    date_string,year,month,day =ds.get_date_string(start_date)

    # Full filepath
    wfr_burst_path = os.path.join(wfr_folder, year, month, day, burst6 + date_string + "*_v*.cdf")
    
    # files are all CDFs for a given day
    cdfs = glob.glob(wfr_burst_path)
    
    no_cdf = len(cdfs)
    print(no_cdf)
    # Define empty list for storing number of records in each CDF
    no_rec = 0

    if (no_cdf>0):

        # j counts every example for each day to append to plot names
        j=0

        for cdf in cdfs:
            j = j+1

            # Open burst file
            burst = pycdf.CDF(cdf)
            # Count how many records on each CDF
            no_rec = no_rec+len(burst['Epoch'])
            print(burst['Epoch'][:])

except pycdf.CDFError:
    print("Doesnt exist file! Move on.")


print(no_rec)