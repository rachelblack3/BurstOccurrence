import numpy as np
import pandas as pd 
import os
from datetime import datetime,timedelta


power_folder = '/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVsPower/'
chorus_folder = '/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVsChorusO/'
new_folder = '/data/emfisis_burst/wip/rablack75/rablack75/CountBurst/CSVsCombined/'

start_date = datetime(year=2014, month=1, day=1)

for chosen_date in (start_date + timedelta(n) for n in range(365)):
    if (chosen_date>datetime(year=2014, month=12, day=31)):
        break
    power_file = power_folder + chosen_date.strftime("%Y") + '/' + chosen_date.strftime("%m") + '/CSVs/' + chosen_date.strftime('%Y%m%d') +'.csv'

    chorus_file = chorus_folder + chosen_date.strftime("%Y") + '/' + chosen_date.strftime("%m") + '/CSVs/' + chosen_date.strftime('%Y%m%d') +'.csv'
    print(chosen_date)
    if ((os.path.exists(power_file))&(os.path.exists(chorus_file))):
        power_data = pd.read_csv(power_file, index_col=False)
        chorus_data = pd.read_csv(chorus_file, index_col=False)

        if (len(power_data)==len(chorus_data)):
            print("cool! Same length")
            # Concatenate columns side-by-side
            # Drop column 'Timestamp' from power
            power_modified = power_data.drop(columns=['Timestamp'])
            power_modified = power_modified.drop(columns=['Unnamed: 0'])
            result = pd.concat([chorus_data, power_modified], axis=1)
            result = result.drop(columns=['Unnamed: 0'])
            print("The columns are",result.columns)
        else:
            continue
        # Change the timestamp to be a datetime object
        result["Timestamp"] = result["Timestamp"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))

        # Create a positive chorus ID flag

        result['chorus_pos'] = None
        for i in range(len(result["Timestamp"])):
            if i % 100 == 0:
                print(i)
            # Convert string to a list by replacing spaces with commas
            chorus_ID = result["ChorusID"][i]
            
            list_string = chorus_ID.replace(' ', ',')
            chorus_list = eval(list_string)
            
            for j in range(len(chorus_list)):
                #print(chorus_list[j])
                if chorus_list[j] == 1.:
                    result.at[i, 'chorus_pos'] = True
                    break
                else:
                    result.at[i, 'chorus_pos'] = False

        result.to_csv(new_folder+"2014/"+str(chosen_date)+'.csv')

    else:
        continue
