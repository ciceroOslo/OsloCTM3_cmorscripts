import numpy as np
import pandas as pd
import xarray as xr
import datetime
import sys

#In the specify_output.py file, set the differemt information regarding the model simulations that
#will be used.
from specify_output import *


#This script read the OsloCTM3 model output and convert it to
#more standardized ouput. This script is adjusted to make the output
#in the format needed in HYway, but can easily be adjusted to other projects.

def read_avgsav(filepath, year,year_out,variable):
    #Read avsavg monthly files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','ihya','ihyb','gridarea', variable]

    #Read all monthly files, add time variable and merge
    for mnd in range(0,12):
        files = f"avgsav_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
        print(files)
        if mnd == 0:
            data = xr.open_dataset(filepath +'/monthly_means/' + files ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            data = data.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
        else:
            print(mnd)
            data_add = xr.open_dataset(filepath +'/monthly_means/' + files ,decode_cf=False,decode_times=False)
            data_add = data_add.get(variable_list)
            data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)


    
    #Rename to standard units
    data.lat.attrs['long_name'] = 'latitude'
    data.lat.attrs['units'] = 'degrees_north'
    data.lon.attrs['long_name'] = 'longitude'
    data.lon.attrs['units'] = 'degrees_east'
    
    return data


long_name_dict = {'airmass':'atmosphere_mass_of_air_per_unit_area'}

complist_ctm_dict = {'airmass':'AIR' }


filepath = filepath + scen+'/'+yr+ '/'


for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    print(filepath)
    
    #Loop trough filenames
    
    comp = 'airmass'
    
    variable_id = comp 
    filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
    print(filename)
    
    variables = complist_ctm_dict[comp]
    print(variables)
    data_field=read_avgsav(filepath,metyear,year_out,variables)
    
    
    data_field[comp]  = data_field[variables]/data_field['gridarea']
    data_field[comp].attrs["unit"] = 'kg m-2'
    
    
    

    
    data_out = data_field[[comp]]
    data_out.attrs = data_field.attrs
    data_out.attrs["history"] = history_text
    data_out.attrs["model_version"] = model_id
    data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

    data_out[comp].attrs['long_name'] = long_name_dict[comp]
    data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
    print('Write to file:')
    print(filename)

    

        


