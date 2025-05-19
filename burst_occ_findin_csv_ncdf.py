""" code that combines the chorus occurence (in pandas dataframe/csv) with all burst power in net CDF"""


"""
1. Chorus occurrence: VA probe A in /data/emfisis_burst/wip/rablack75/rablack75/CountSurvey/CSVschorus_surveypowerA
2. Power in all bands at: VA probe A in /data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/bug 
"""

"""
STEPS outside loop
1. define root folders for both
2. inside chosen year, the occurence file format required /month/CSVs/{yyyymmdd}.csv, the power file format is /month/power_{yyyymmdd}.nc
STEPS inside loop
1. Load the NetCDF file and read its dimensions.
2. Load the CSV file and ensure the x values from the CSV file correspond to those in the NetCDF file.
3. Align the x dimension from the CSV with the NetCDF dataset based on matching values.
4. Merge the two datasets along the x dimension by adding the values from the CSV into the NetCDF.
"""

import numpy as np
import pandas as pd
import xarray as xr
import os

from datetime import datetime,timedelta

""" functions """

''' to_dt: function that changes timestamp in format 'nanoseconds since 1970 --> datetime.datetime'''
def to_dt(nanoseconds_value):

    # Convert nanoseconds to seconds
    seconds_value = nanoseconds_value / 1e9

    # Unix epoch
    epoch = datetime(1970, 1, 1)

    # Convert to datetime
    human_readable_datetime = epoch + timedelta(seconds=seconds_value)
    
    return human_readable_datetime

''' check_last_8_digits_match: checks if the last 8 digits of two files (before extension) match '''
def check_last_8_digits_match(file1, file2):
    # Get the base filenames (without directory paths)
    base1 = os.path.basename(file1)
    base2 = os.path.basename(file2)
    
    # Remove the file extension using os.path.splitext
    name1, _ = os.path.splitext(base1)
    name2, _ = os.path.splitext(base2)
    
    # Get the last 8 characters of the filenames
    last_8_file1 = name1[-8:]
    last_8_file2 = name2[-8:]
    
    # Check if they match
    return last_8_file1 == last_8_file2, last_8_file1, last_8_file2


years = [2019]

for year in years:
    occ_root = f'/data/emfisis_burst/wip/rablack75/rablack75/CountSurvey/CSVschorus_surveypowerA/{year}'                
    power_root = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/{year}'   

    output_root = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/occ_pow_test/{year}'
    if not os.path.exists(output_root): 
        # if the directory is not present  
        # then create it. 
        os.makedirs(output_root)

    # List of CSV files
    occ_file_list = []
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(occ_root):
        for filename in filenames:
            # Construct the full file path and append it to the list
            occ_file_list.append(os.path.join(dirpath, filename))


    # List of CSV files
    power_file_list = []
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(power_root):
        for filename in filenames:
            # Construct the full file path and append it to the list
            power_file_list.append(os.path.join(dirpath, filename))


    for power_file in power_file_list:
        for occur_file in occ_file_list:

            match,date1,date2 = check_last_8_digits_match(power_file,occur_file)
            
            if match:
                
                #start the joining!
                print(date1,date2)
                # use pandas to read occurence into dataframe (df)
                df = pd.read_csv(occur_file)
                
                # use xarray to read power into dataset (ds)
                ds = xr.open_dataset(power_file)
            
                """ change the epochs from ns since 1960 to np.datetime64 """

                netcdf_t = xr.apply_ufunc(
                    to_dt,  # The function to apply
                    ds["timestamp"],                 # The xarray DataArray
                    vectorize=True                   # Whether to vectorize the function (applies to each element)
                )
                datetime_list=netcdf_t.values          # save the values

                df["Timestamp64"] = df["Timestamp"].apply(np.datetime64)


                ds["chorus_flag"] = (("x", "y"), np.zeros((len(datetime_list),10)))
                ds['MLT'] = (('x',), np.zeros(len(datetime_list)))
                ds['MLAT'] = (('x',), np.zeros(len(datetime_list)))
                ds['Lstar'] = (('x',), np.zeros(len(datetime_list)))
                ds['AE'] = (('x',),np.zeros(len(datetime_list)))
                ds['Kp'] = (('x',), np.zeros(len(datetime_list)))
                ds['Dst'] = (('x',), np.zeros(len(datetime_list)))

                # loop through all burst power records on a given day
                for i in range(len(datetime_list)):
                    for k in range(len(df["Timestamp"])-1):
                
                        if df["Timestamp64"][k]<=datetime_list[i]<df["Timestamp64"][k+1]:
                            ds["MLT"].loc[i] = df["MLT"][k]
                            ds["MLAT"].loc[i] = df["MLAT"][k]
                            ds["Lstar"].loc[i] = df["Lstar"][k]
                            ds["AE"].loc[i] = df["AE"][k]
                            ds["Kp"].loc[i] = df["Kp"][k]
                            ds["Dst"].loc[i] = df["Dst"][k]

                            # Convert string to a list by replacing spaces with commas

                            chorus_ID = df["ChorusID"][k]
                            list_string = chorus_ID.replace(' ', ',')
                            chorus_list = eval(list_string)
                            
                            for j in range(len(chorus_list)):

                                # 0.9 - 1 fce
                                if (j>=int(9*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 9] = 1.  

                                # 0.8 - 0.9 fce
                                if ((int(8*len(chorus_list)/10))<=j<int((9*len(chorus_list)/10))) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 8] = 1.

                                # 0.7 - 0.8 fce
                                if (int(7*len(chorus_list)/10)<=j<int(8*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 7] = 1.

                                # 0.6 - 0.7 fce
                                if (int(7*len(chorus_list)/10)<=j<int(8*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 6] = 1.

                                # 0.5 - 0.6 fce
                                if (int(5*len(chorus_list)/10)<=j<int(6*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 5] = 1.
                                # 0.4 - 0.5 fce
                                if (int(4*len(chorus_list)/10)<=j<int(5*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 4] = 1.

                                # 0.3 - 0.4 fce
                                if (int(3*len(chorus_list)/10)<=j<int(4*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 3] = 1.

                                # 0.2 - 0.3 fce
                                if (int(2*len(chorus_list)/10)<=j<(3*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 2] = 1.
                                
                                # 0.1 - 0.2 fce
                                if (int(1*len(chorus_list)/10)<=j<int(2*len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 1] = 1.

                                if (j<int(len(chorus_list)/10)) and (chorus_list[j] == 1.):
                                    ds["chorus_flag"].loc[i, 0] = 1.
                                    continue

                            print(i, "done")
                        else:
                            continue    

            
                print(date1,"is done")
                # Save the modified dataset to a new NetCDF file
                output_file = output_root+f'/combined_{date1}.nc'
                #print(ds.head())
                ds.to_netcdf(output_file)

                print(f"Combined dataset saved")
