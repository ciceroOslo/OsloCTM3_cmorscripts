import numpy as np
import pandas as pd
import xarray as xr
import datetime
import sys


#This script read the OsloCTM3 model output and convert it to
#more standardized ouput. This script is adjusted to make the output
#in the format needed in HYway, but can easily be adjusted to other projects.

def read_scavenging_2d(filepath,year,year_out,variable_out,variables):
    variable_list = ['lat','lon'] + variables 
    print(variable_list)

    dom = [31,28,31,30,31,30,31,31,30,31,30,31]
    for mnd in range(1,13):
        for day in range(1,dom[mnd-1]+1):
            files = "scavenging_daily_2d_"+ str(year)+ str(mnd).zfill(2)+str(day).zfill(2)+ ".nc"
            print(files)
            if mnd == 1 and day == 1:
                data = xr.open_dataset(filepath +'/scavenging_daily/' + files ,decode_cf=False,decode_times=False)
                gridarea = data['gridarea']
                data = data.get(variable_list)
                data = data.expand_dims(time=[datetime.datetime(year_out,mnd,day)])
                data[variable_out] = data[variables[0]]/(gridarea*24.*60.*60.) + data[variables[1]]/(gridarea*24.*60.*60.) #unit kg m-2 s-1
            else:
                print(mnd)
                data_add = xr.open_dataset(filepath +'/scavenging_daily/' + files ,decode_cf=False,decode_times=False)
                data_add = data_add.get(variable_list)
                data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd,day)])
                data_add[variable_out] = data_add[variables[0]]/(gridarea*24.*60.*60.) + data_add[variables[1]]/(gridarea*24.*60.*60.)  #unit kg m-2 s-1
                data = data.merge(data_add)


    data[variable_out].attrs['unit'] = 'kg m-2 s-1'            
    print(data)
    
    monthly_mean = data[variable_out].resample(time='M').mean().to_dataset()
    monthly_mean.attrs = data.attrs

    monthly_mean.lat.attrs['units'] = 'degrees_north'
    monthly_mean.lon.attrs['units'] = 'degrees_east' 

    return monthly_mean


long_name_dict = {'wethcho' : 'Wet deposition rate of formaldehyde',	
                  'wetch3oh': 'Wet deposition rate of methanol',	
                  'wetmhp': 'Wet deposition rate of methyl hydroperoxide',	
                  'wetso4': 'Wet deposition rate of sulphate',	
                  'wetnh3': 'Wet deposition rate of ammonia',
                  'wethcooh': 'Wet deposition rate of formic acid',
                  'wetch3cooh': 'Wet deposition rate of acetic acid'}	

complist_dict = {'wethcho' : 'CH2O',	
                  'wetch3oh': 'CH3OH',	
                  'wetmhp': 'CH3O2H',	
                  'wetso4': 'SO4',	
                  'wetnh3': 'NH3'} #,
                  #'wethcooh': 'none',
                  #'wetch3cooh': 'none'}

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
scen = 'TEST_CTM3/CTM3_test_drydep'
yr = ''

filepath = '/div/qbo/users/ragnhibs/AlternativeFuels/methanol/CTM3results/'+scen+'/'+yr+ '/'

metyear_list = [2009]

for m,metyear in enumerate(metyear_list):
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    for comp in complist_dict:
        print(comp)
        variable_id = comp 
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'

        print(filename)

        variables = ['ls_' + complist_dict[comp],'cnv_' + complist_dict[comp]]

        print(filepath)
        data_field = read_scavenging_2d(filepath,year,year_out,comp,variables)

        data_out = data_field[[comp]]
        data_out.attrs["history"] = history_text
        data_out[comp].attrs['long_name'] = long_name_dict[comp]

        print(data_out)
        
        print('Write to file:')
        print(filename)
    
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
      
        print(data_field)

