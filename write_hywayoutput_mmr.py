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

def read_avgsav(filepath, year,year_out,variables):
    #Read avsavg monthly files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','ihya','ihyb','AIR'] +  variables

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


def calc_mmr(data_field,variable,variable_out):
    #Calculate mmr


    data_field = data_field.assign(varout=data_field[variable]/data_field['AIR'])
    data_field.varout.attrs['units'] = 'kg kg-1'

    #name the variable
    data_field = data_field.rename(varout=variable_out)

    return data_field

long_name_dict = {'mmroa' : 'mass_fraction_of_particulate_organic_matter_dry_aerosol_particles_in_air',
                  'mmrso4': 'mass_fraction_of_sulfate_dry_aerosol_particles_in_air',
                  'mmrno3fine': 'mass_fraction_of_fine_mode_nitrate_dry_aerosol_particles_in_air'}

oacomplist=['omBB1fob','omBB1fil',
            'omFF1fob','omFF1fil',
            'omBF1fob','omBF1fil',
            'omOCNfob','omOCNfil', 
            'SOAAER11','SOAAER21','SOAAER31','SOAAER41','SOAAER51', 
            'SOAAER12','SOAAER22','SOAAER32','SOAAER42','SOAAER52', 
            'SOAAER13','SOAAER23','SOAAER33','SOAAER43','SOAAER53',
            'SOAAER61','SOAAER62', 
            'SOAAER71','SOAAER72',
            'SOAAER81','SOAAER82']


complist_ctm_dict = {'mmroa'  : oacomplist,
                     'mmrso4'	: ['SO4'],
                     'mmrno3fine': ['NO3fine']}
                    

#Specify outputpath
outputpath = '/div/no-backup/users/ragnhibs/HYway/OsloCTM3output/'

#Experiment and simulation infor:
table_id = 'monthly'
model_id = 'OsloCTM3-vtest'
experiment_id = 'transient2010s'
project_id = 'hyway'
member_id = 'r1'

history_text = 'OsloCTM3 simulations for HYway, contact: r.b.skeie@cicero.oslo.no'

#Raw model output 
scen = 'TEST_CTM3/CTM3_hyway_test2010_newvocemis' 
yr = ''

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
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
        print(filename)

        variables = complist_ctm_dict[comp]
        print(variables)
        data_field=read_avgsav(filepath,metyear,year_out,variables)

        for v,var in enumerate(variables):
            if v ==0:
                print(var)
                data_field = calc_mmr(data_field,var,comp)
                print(data_field)
            else:
                print(var)
                data_field = calc_mmr(data_field,var,'tmp')
               
                data_field[comp] = data_field[comp] + data_field['tmp']
                data_field = data_field.drop_vars('tmp')
                
        
        
        data_out = data_field[['ihya','ihyb',comp]]
        data_out[comp].attrs['units'] = 'kg kg-1'
        data_out.attrs = data_field.attrs
        data_out.attrs["history"] = history_text
        data_out.attrs["model_version"] = model_id
        data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 


        data_out[comp].attrs['long_name'] = long_name_dict[comp]
        data_out[comp].attrs['original_components'] = '_'.join(variables)
        print(data_out)

        print('Write to file:')
        print(filename)
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
        


