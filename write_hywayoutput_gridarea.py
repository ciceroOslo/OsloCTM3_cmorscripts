import numpy as np
import pandas as pd
import xarray as xr
import datetime
#import matplotlib.pyplot as plt
import sys
#from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
#                               AutoMinorLocator)


#This script read the OsloCTM3 model output and convert it to
#more standardized ouput. This script is adjusted to make the output
#in the format needed in HYway, but can easily be adjusted to other projects.

def read_avgsav_onemonth(filepath, year,year_out,variables):
    #Read avsavg monthly files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','ihya','ihyb','AIR'] +  variables

    #Read all monthly files, add time variable and merge
    mnd = 0
    files = f"avgsav_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
    print(files)
    
    data = xr.open_dataset(filepath +'/monthly_means/' + files ,decode_cf=False,decode_times=False)
    data = data.get(variable_list)
    
    #Rename to standard units
    data.lat.attrs['long_name'] = 'latitude'
    data.lat.attrs['units'] = 'degrees_north'
    data.lon.attrs['long_name'] = 'longitude'
    data.lon.attrs['units'] = 'degrees_east'
    
    return data


long_name_dict = {'areacella':'Area of grid cell'}


complist_ctm_dict = {'areacella': 'gridarea'}


#Specify outputpath
outputpath = '/div/no-backup/users/ragnhibs/HYway/OsloCTM3output/'

#Experiment and simulation infor:
table_id = 'fixed'
model_id = 'OsloCTM3-vtest'
experiment_id = 'transient2010s'
project_id = 'hyway'
member_id = 'r1'

history_text = 'OsloCTM3 simulations for HYway, contact: r.b.skeie@cicero.oslo.no'

#Raw model output 
scen = 'CNTR_v2'
yr = 'YR1'

filepath = '/div/qbo/users/ragnhibs/AlternativeFuels/methanol/CTM3results/'+scen+'/'+yr+ '/'

metyear_list = [2009]

for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    print(filepath)

    #Loop trough filenames
    for comp in complist_ctm_dict:
        
        variable_id = comp 
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id  +'.nc'

        print(filename)

        variables = complist_ctm_dict[comp]
        print(variables)
        data_field=read_avgsav_onemonth(filepath,metyear,year_out,[variables])
        data_field = data_field.rename({'gridarea':comp})
        print(data_field)
        
        data_out = data_field[[comp]]
        data_out.attrs = data_field.attrs
        data_out.attrs["history"] = history_text
        data_out[comp].attrs['long_name'] = long_name_dict[comp]

        print(data_out)

        print('Write to file:')
        print(filename)
        data_out.to_netcdf(filename)
        


