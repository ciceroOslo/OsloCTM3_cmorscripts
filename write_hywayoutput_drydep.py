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


#Check if variable is in the prod-loss output
def chech_if_drydep_exist(filepath,year,year_out,variable_out,variable):
    variable_list = ['lat','lon',variable] 
    print(variable_list)
    
    mnd=1
    day=1
    files = "scavenging_daily_2d_"+ str(year)+ str(mnd).zfill(2)+str(day).zfill(2)+ ".nc"
    
    data = xr.open_dataset(filepath +'/scavenging_daily/' + files ,decode_cf=False,decode_times=False)
    
    isdata = True
        
    if variable in data.variables:
        print(f"Variable '{variable}' is present in the dataset.")
        isdata = True
    else:
        print(f"Variable '{variable}' is not present in the dataset.")
        isdata = False
        
    return isdata


def read_scavenging_2d(filepath,year,year_out,variable_out,variable):
    variable_list = ['lat','lon',variable] 
    print(variable_list)

    dom = [31,28,31,30,31,30,31,31,30,31,30,31]
    for mnd in range(1,13):
        for day in range(1,dom[mnd-1]+1):
            files = "scavenging_daily_2d_"+ str(year)+ str(mnd).zfill(2)+str(day).zfill(2)+ ".nc"
            #print(files)
            if mnd == 1 and day == 1:
                data = xr.open_dataset(filepath +'/scavenging_daily/' + files ,decode_cf=False,decode_times=False)
                gridarea = data['gridarea']
                data = data.get(variable_list)
                data = data.expand_dims(time=[datetime.datetime(year_out,mnd,day)])
                data[variable_out] = data[variable]/(gridarea*24.*60.*60.)  #unit kg m-2 s-1
            else:
                print(mnd)
                data_add = xr.open_dataset(filepath +'/scavenging_daily/' + files ,decode_cf=False,decode_times=False)
                data_add = data_add.get(variable_list)
                data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd,day)])
                data_add[variable_out] = data_add[variable]/(gridarea*24.*60.*60.)  #unit kg m-2 s-1
                data = data.merge(data_add)


    data[variable_out].attrs['unit'] = 'kg m-2 s-1'            
    print(data)
    
    monthly_mean = data[variable_out].resample(time='M').mean().to_dataset()
    monthly_mean.attrs = data.attrs

    monthly_mean.lat.attrs['units'] = 'degrees_north'
    monthly_mean.lon.attrs['units'] = 'degrees_east' 

    return monthly_mean



long_name_dict = {'drych3cooh'	:'tendency_of_atmosphere_mass_content_of_acetic_acid_due_to_dry_deposition',
                  'drych3coch3'	:'tendency_of_atmosphere_mass_content_of_acetone_due_to_dry_deposition',
                  'dryco'   	:'tendency_of_atmosphere_mass_content_of_carbon_monoxide_due_to_dry_deposition',
                  'dryc2h6'	:'tendency_of_atmosphere_mass_content_of_ethane_due_to_dry_deposition',
                  'dryc2h4'	:'tendency_of_atmosphere_mass_content_of_ethene_due_to_dry_deposition',
                  'dryc2h2'	:'tendency_of_atmosphere_mass_content_of_ethyne_due_to_dry_deposition',
                  'dryhcho'	:'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_dry_deposition',
                  'dryhcooh'	:'tendency_of_atmosphere_mass_content_of_formic_acid_due_to_dry_deposition',
                  'drychocho'	:'tendency_of_atmosphere_mass_content_of_glyoxal_due_to_dry_deposition',
                  'dryisop'	:'tendency_of_atmosphere_mass_content_of_isoprene_due_to_dry_deposition',
                  'drych4'	:'tendency_of_atmosphere_mass_content_of_methane_due_to_dry_deposition',
                  'drych3oh'	:'tendency_of_atmosphere_mass_content_of_methanol_due_to_dry_deposition',
                  'drymhp'	:'tendency_of_atmosphere_mass_content_of_methyl_hydroperoxide_due_to_dry_deposition',
                  'dryh2'	:'tendency_of_atmosphere_mass_content_of_molecular_hydrogen_due_to_dry_deposition',
                  'dryo3'	:'tendency_of_atmosphere_mass_content_of_ozone_due_to_dry_deposition',
                  'drypan'	:'tendency_of_atmosphere_mass_content_of_pan_due_to_dry_deposition'}



complist_dict = {'dryh2' : 'H2',	
                 'drych3coch3' :'ACETONE',
                 'dryo3':'O3',
                 'dryco':'CO',
                 'drychocho': 'HCOHCO',
                 'dryisop' : 'ISOPRENE',
                 #'drych4':'CH4',
                 'dryhcho':'CH2O',	
                 'drych3oh':'CH3OH',
                 'drymhp':'CH3O2H',
                 'dryc2h6':'C2H6',
                 'dryc2h4':'C2H4',
                 'drypan':'PANX',
                 'drych3cooh':'CH3COOH',
                 'dryc2h2':'C2H2',
                 'dryhcooh':'HCOOH'}




filepath = filepath +scen+'/'+yr+ '/'

for m,metyear in enumerate(metyear_list):
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    for comp in complist_dict:
        print(comp)
        variable_id = comp 
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'

        print(filename)

        variable = 'dry_' + complist_dict[comp]

        print(filepath)

        isdata = chech_if_drydep_exist(filepath,year,year_out,comp,variable)

                
        if isdata:
            data_field = read_scavenging_2d(filepath,year,year_out,comp,variable)

            data_out = data_field[[comp]]
            data_out.attrs["history"] = history_text
            data_out.attrs["model_version"] = model_id
            data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

            data_out[comp].attrs['long_name'] = long_name_dict[comp]
            
            #print(data_out)
            
            print('Write to file:')
            print(filename)
            
            data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
      
            #print(data_field)

