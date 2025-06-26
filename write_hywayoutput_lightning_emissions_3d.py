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


#Todo NOx, add list of components included in combined variables. 

def read_emis_accumulated(filepath,year,year_out,variable_out,variable):
    variable_list = ['lat','lon','lev','gridarea','delta_time', variable]
    for mnd in range(0,12):
        files = f"emis_accumulated_3d_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
        print(files)
        if mnd == 0:
            data = xr.open_dataset(filepath +'/emissions/' + files ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            data = data.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
        else:
            print(mnd)
            data_add = xr.open_dataset(filepath +'/emissions/' + files ,decode_cf=False,decode_times=False)
            data_add = data_add.get(variable_list)
            data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)

    data.lat.attrs['long_name'] = 'latitude'
    data.lon.attrs['long_name'] = 'longitude'

    #NB delta_time in the OsloCTM3 output is wrong. Recalculate it here.
    days_in_month = data.time.dt.days_in_month
    data['delta_time'] = days_in_month*60.0*60.0*24.0
              
    data[variable_out] = data[variable]/(data['gridarea']*data['delta_time'])
    data[variable_out].attrs['unit'] = 'kg m-2 s-1'
         
    
    return data

long_name_dict = {'emilno':'tendency_of_atmosphere_moles_of_no_due_to_lightning'}
long_name_dict_kg = {'emilno':'tendency_of_atmosphere_no_due_to_lightning'}


complist_dict = {'emilno': 'NO'}

filepath = filepath +scen+'/'+yr+ '/'
filepath_wo_lno = filepath_wo_lno  +scen+'/'+yr+ '/'


for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    for comp in complist_dict:
        print(comp)
        variable_id = comp + '3D'
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
        print(filename)
        variable=complist_dict[comp]
        print(variable)
        #First I have to read kg emissions of NO
        #Units should be mol s-1
        
        data_field = read_emis_accumulated(filepath,metyear,year_out,comp,variable)
        data_field_wo_lno = read_emis_accumulated(filepath_wo_lno,metyear,year_out,comp,variable)

        data_field['TotNO'] = data_field[comp]
        data_field[comp] = data_field[comp] - data_field_wo_lno[comp]
        data_field[comp].attrs['unit'] = 'kg m-2 s-1'
        print(data_field[comp])

    
        
        data_out = data_field[[comp]]
        
        data_out.attrs["history"] = history_text
        data_out.attrs["model_version"] = model_id
        data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        data_out[comp].attrs['long_name'] = long_name_dict_kg[comp]

        print(data_out)
        
        print('Write to file:')
        print(filename)
    
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})

    



        

        #Convert to mol per sec
        variable_id = comp
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
        print(filename)
        variable=complist_dict[comp]
        print(variable)

        data_mol = data_field.copy()
        
        data_mol[comp] = data_out[comp].sum(dim='lev')*data_field['gridarea']/30.010*1000.0 #g/mol
        data_mol[comp].attrs['unit'] = 'mol s-1'

        data_out = data_mol[[comp]]
        data_out.attrs["history"] = history_text
        data_out.attrs["model_version"] = model_id
        data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        data_out[comp].attrs['long_name'] = long_name_dict[comp]

        print(data_out)
        
        print('Write to file:')
        print(filename)
          
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})



        #Excluding lightning NO:
        comp = 'emino'
        variable_id = comp
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'

        data_field[comp] =  data_field['TotNO'] - data_field['emilno']
        
        print(data_field)
    
        data_field[comp] = data_field[comp].sum(dim='lev')
        data_field[comp].attrs['unit'] = 'kg m-2 s-1'
        data_field[comp].attrs['long_name'] = 'tendency_of_atmosphere_mass_content_of_nitric oxide_due_to_emission'

        
        data_out2 = data_field[[comp]]
        data_out2.attrs["history"] = history_text
        data_out2.attrs["model_version"] = model_id
        data_out2.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

       


        print(data_out)
        
        print('Write to file:')
        print(filename)
          
        data_out2.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})

        
        exit()
