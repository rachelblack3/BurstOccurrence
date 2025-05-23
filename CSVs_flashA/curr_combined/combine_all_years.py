# Combine all of the year folders together into one .nc file "full_{start_year}_{end year}"
import xarray as xr

# What years do you want?
years = [2013,2014,2015,2016,2017,2018,2019] 
# file header
flnm_root = '/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/curr_combined/full_'

# make list of all files
file_list=[]
for year in years:

    file_list.append(flnm_root+f'{year}.nc')
print(file_list)

# open all of the files as xarrays, and ave to list
datasets = [xr.open_dataset(file) for file in file_list]
# Concatenate along the 'x' dimension
combined_dataset = xr.concat(datasets, dim='x')
combined_dataset.to_netcdf('/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/curr_combined/full_13_19.nc')