""" code that combines the chorus occurence (in pandas dataframe/csv) with all burst power in net CDF"""


"""
1. Chorus occurrence: VA probe A in /data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVsChorusO
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


years = [2012,2013,2014,2015,2016,2017,2018,2019]

for year in years:
    occ_root = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVsChorusO/{year}'                
    power_root = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/bug/{year}'   

    output_root = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/combined_with_occ/{year}'
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

                df['chorus_pos'] = 0.
                df['upper'] = 0.
                df['lower'] = 0.

                

                for i in range(len(df["Timestamp"])):
                    # Convert string to a list by replacing spaces with commas

                    chorus_ID = df["ChorusID"][i]
                    list_string = chorus_ID.replace(' ', ',')
                    chorus_list = eval(list_string)
                    
                    for j in range(len(chorus_list)):
                        #print(chorus_list[j])
                        if (j>=(len(chorus_list)/2)) and (chorus_list[j] == 1.):
                            df.at[i, 'chorus_pos'] = 1.
                            df.at[i,'upper'] = 1.
                        if (j<(len(chorus_list)/2)) and (chorus_list[j] == 1.):
                            df.at[i, 'chorus_pos'] = 1.
                            df.at[i,'lower'] = 1.
                        # break
                        #else:
                            #df.at[i, 'chorus_pos'] = 0.           

                    #if (df["chorus_pos"][i]==1.) and (df["MLT"][i]<6):
                     #   print("HERE!",df["Timestamp"][i],df['MLT'][i])
                # Assuming the CSV has columns 'x' and 'values', where 'x' matches the NetCDF x-dimension
                # Ensure both datasets use the same x-dimension name
                csv_t = df['Timestamp'].values     # Extract the x values from the CSV file

                # Ensure CSV and NetCDF are aligned based on the x-dimension
                # Reorder the CSV values based on matching x-values with the NetCDF

                df_sorted = df.set_index('Timestamp64').reindex(datetime_list).reset_index()
               
                for i in range(len(df_sorted["Timestamp64"])):
                    if (df_sorted["chorus_pos"][i]==1.) and (df_sorted["MLT"][i]<6):
                        print("HERE!",df_sorted["Timestamp64"][i],df_sorted['MLT'][i])
                
                # Add the CSV 'values' column as a new data variable to the NetCDF dataset
                # Assuming the 'values' from the CSV is a 1D array and needs to be added as a new variable
                ds['chorus_ID'] = (('x',), df_sorted['chorus_pos'].values)
                ds['upper'] = (('x',), df_sorted['upper'].values)
                ds['lower'] = (('x',), df_sorted['lower'].values)
                ds['MLT'] = (('x',), df_sorted['MLT'].values)
                ds['MLAT'] = (('x',), df_sorted['MLAT'].values)
                ds['Lstar'] = (('x',), df_sorted['Lstar'].values)
                ds['AE'] = (('x',), df_sorted['AE'].values)
                ds['Kp'] = (('x',), df_sorted['Kp'].values)
                ds['Dst'] = (('x',), df_sorted['Dst'].values)

                # Save the modified dataset to a new NetCDF file
                output_file = output_root+f'/combined_{date1}v2.nc'
                #print(ds.head())
                ds.to_netcdf(output_file)

                print(f"Combined dataset saved")
