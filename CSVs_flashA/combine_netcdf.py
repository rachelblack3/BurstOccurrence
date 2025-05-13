import xarray as xr
import os

# Directory containing the NetCDF files

years = [2017,2018]

for target_year in years:
    input_dir = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/occ_pow_test/{target_year}'
    output_file = f'/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVs_flashA/curr_combined/full_{target_year}.nc'

    # Loop through each month subdirectory and collect NetCDF files
    file_list = []
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            #if filename.endswith(".nc"):
            # Construct the full file path and append it to the list
            file_list.append(os.path.join(dirpath, filename))

    datasets = [xr.open_dataset(file) for file in file_list]
    #print(datasets[-11].head())
    # Concatenate along the 'x' dimension
    combined_dataset = xr.concat(datasets, dim='x')
    print(combined_dataset.head())
        # Save the combined dataset to a new NetCDF file
    combined_dataset.to_netcdf(output_file)

    print(f'Year: {target_year} done')