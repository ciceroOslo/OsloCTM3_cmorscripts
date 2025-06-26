import numpy as np
import pandas as pd
import xarray as xr
import datetime
import sys

#In the specify_output.py file, set the differemt information regarding the model simulations that
#will be used.
from specify_output_3hrs import *

#This script read the OsloCTM3 model output and convert it to
#more standardized ouput. This script is adjusted to make the output
#in the format needed in HYway, but can easily be adjusted to other projects.

def read_3hrs(filepath,fileprefix, year):
    #Read 3hry files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','time','srfacepres','geopothght']
    print(filepath)
    
    #Read all monthly files, add time variable and merge
    for day in range(0,365): #66):
        files = f"{fileprefix}{year}_{day+1:03}.nc"
        print(files)
        
        if day == 0:
            data = xr.open_dataset(filepath +'/'+fileprefix+'/' + files ) # ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            print(data)
                        
        else:
            data_add = xr.open_dataset(filepath +'/'+fileprefix+'/' + files ) # ,decode_cf=False,decode_times=False)
            data_add = data_add.get(variable_list)
            #data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)
            print(data)
           

    #Rename to standard units
    #data.lat.attrs['long_name'] = 'latitude'
    #data.lat.attrs['units'] = 'degrees_north'
    #data.lon.attrs['long_name'] = 'longitude'
    #data.lon.attrs['units'] = 'degrees_east'
    
    return data

def read_avgsav(filepath, year):
    #Read avsavg monthly files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','ihya','ihyb']
    mnd = 0
    files = f"avgsav_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
    data = xr.open_dataset(filepath +'monthly_means/'+ files ) # ,decode_cf=False,decode_times=False)
    data = data.get(variable_list)

    return data


    

def calc_pfull(data,data_monthly):
    print(data)

    #For initialization
    data['pfull'] = data['zg']*0.0
   
    for l,lev in enumerate(data.lev):
        data['pfull'].isel(lev=l)[:] = 0.5*(data_monthly['ihya'].isel(ilev=l) + data_monthly['ihyb'].isel(ilev=l)*data['srfacepres'] + data_monthly['ihya'].isel(ilev=l+1) + data_monthly['ihyb'].isel(ilev=l+1)*data['srfacepres'] )

    
        
    return data




long_name_dict = {'pfull':'air_pressure',
                  'zg': 'geopotential_height'}


complist_ctm_dict = {'ps':'srfacepres',
                     'zg':'geopothght'}


filepath = filepath + scen+'/'+yr+ '/'


for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear

    
    

    time_range = str(year)+ '01-' + str(year) + '12'

    print(filepath)

    #Loop trough filenames
    #for comp in complist_ctm_dict:
        
    variable_id = 'zg'
    filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
    print(filename)

        
    

    fileprefix = 'zgh'


        
    data_field=read_3hrs(filepath,fileprefix,year)
    print(data_field)
    
    
    comp = 'zg'
    variable = complist_ctm_dict[comp]
    
    data_field = data_field.rename({variable: comp})

    print(data_field)
    
    data_out = data_field[[comp]]
    data_out.attrs = data_field.attrs
    data_out.attrs["history"] = history_text
    data_out.attrs["model_version"] = model_id
    data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            
    data_out[comp].attrs['long_name'] = long_name_dict[comp]
            
    print(data_out)
            
    print('Write to file:')
    print(filename)
    data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})



    comp = 'pfull'
    variable_id = comp
    filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
    print(comp)

    #variable = complist_ctm_dict[comp]
    #data_field = data_field.rename({variable: comp})
    print(data_field)
    
    #For vertical coord.
    data_monthly = read_avgsav(filepath, year)

    data = calc_pfull(data_field,data_monthly)

    print(data)

    data_out = data[[comp]]
    data_out[comp] = data_out[comp]*100.0 #hPa -> Pa
    data_out[comp].attrs["unit"]='Pa'
    data_out.attrs = data.attrs
    data_out.attrs["history"] = history_text
    data_out.attrs["model_version"] = model_id
    data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            
    data_out[comp].attrs['long_name'] = long_name_dict[comp]
            
    print(data_out)
            
    print('Write to file:')
    print(filename)
    data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})


    
    exit()
