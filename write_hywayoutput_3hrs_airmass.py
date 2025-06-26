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

def read_3hrs(filepath,fileprefix, year,variable):
    #Read 3hry files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','time',variable]
    print(filepath)
    
    #Read all monthly files, add time variable and merge
    for day in range(0,365):
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


def calc_vmr(data_field,variable,variable_out):
    #Calculate vmr, output mol/mol

    #Find molecular weight
    molecw = find_molecw(variable)

    data_field = data_field.assign(varout=data_field[variable]/data_field['AIR']*28.97/molecw)
    data_field.varout.attrs['units'] = 'mol/mol'

    #name the variable
    data_field = data_field.rename(varout=variable_out)

    return data_field


def find_molecw(variable):
    #Find molecular weight for given variable

    #Read input file used in the CTM
    tracer_file = 'input/tracer_list_all_h2.d'
    header_list = ["TracerNumber","TCNAME","TCMASS","Comments"]
    df_tracer = pd.read_csv(tracer_file,skiprows=3,sep="\'",usecols=[0,1,2,3],names=header_list)

    molecw =df_tracer.loc[df_tracer['TCNAME'] == variable]['TCMASS'].values 

    return molecw


long_name_dict = {'airmass':'atmosphere_mass_of_air_per_unit_area'}

complist_ctm_dict = {'airmass'       : 'air_densit'}

filepath = filepath + scen+'/'+yr+ '/'

for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear


    time_range = str(year)+ '01-' + str(year) + '12'

    print(filepath)

    #Loop trough filenames
    for comp in complist_ctm_dict:
        
        variable_id = comp 
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
        print(filename)

        
        variable = complist_ctm_dict[comp]

        fileprefix = 'air'

        data_field=read_3hrs(filepath,fileprefix,year,variable)

        print(data_field)

       
        data_field = data_field.rename({variable: comp})
                                       
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
        


