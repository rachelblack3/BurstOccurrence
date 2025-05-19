# BurstOccurrence
Code that finds chorus waves in survey data, to then match the events to timestamps in the burst. The occurrence of chorus in the burst can then be saved.

Rundown of files:

_**/CSVs_flashA/year/month**_:
This contains all of the burst files, in year/month/day.nc, after being FFT's appropriatley on the HPC, and sent back to my storage. Chorus has not yet been ID'd.

_**/CSVs_flashA/occ_pow_test/**_:
This contains all of the chorus events found in the survey that have a corresponding burst event. This was created using **_burst_occ_findin_csv_ncdf.py_**, which cycles through the survey chorus pccurence on Van Allen A, and finds the corrrepsonding times in burst.

**_/CSVs_flashA/curr_combined/_**:
This combines all files from occ_pow_test into larger yearly .nc files, for easier reading later.



