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

def read_prod_loss(filepath, year, year_out,variable):
    variable_list = ['lat','lon','lev','delta_time',variable]

    print(variable_list)
   
    for mnd in range(0,12):
        files = f"chemistryPL_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
        print(filepath + files)
        
        if mnd == 0:
            data = xr.open_dataset(filepath +'/' + files ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            data[variable] = data[variable]/data['delta_time'] #kg per gridbox per sec.
            
            data = data.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])

        else:
            data_add = xr.open_dataset(filepath +'/' + files ,decode_cf=False,decode_times=False)
            data_add = data_add.get(variable_list)
            data_add[variable] = data_add[variable]/data_add['delta_time'] #kg per gridbox per sec.
            data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)

    data.lat.attrs['long_name'] = 'latitude'
    data.lon.attrs['long_name'] = 'longitude'

    data[variable].attrs['unit'] = 'kg s-1'
    
    return data


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

    #Keep in 3D
    data[variable_out] = data[variable]/data['delta_time']
    data[variable_out].attrs['unit'] = 'kg s-1'
    data = data.drop(variable)
          
    
    return data


def read_avgsav_volume(filepath, year,year_out):
    #Read avsavg monthly files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','ihya','ihyb','volume']

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


long_name_dict = {#'prodo3':'tendency_of_atmosphere_mass_content_of_ozone_due_to_chemical_production',
                  #'losso3':'tendency_of_atmosphere_mass_content_of_ozone_due_to_chemical_destruction',
                  'prodh2':'tendency_of_atmosphere_mass_content_of_molecular_hydrogen_due_to_chemical_production',
                  'lossh2':'tendency_of_atmosphere_mass_content_of_molecular_hydrogen_due_to_chemical_destruction',
                  'lossch4':'tendency_of_atmosphere_mass_content_of_methane_due_to_chemical_destruction_by_hydroxyl_radical',
                  'prodco':'tendency_of_atmosphere_mass_content_of_carbon_monoxide_due_to_chemical_production',
                  'lossco':'tendency_of_atmosphere_mass_content_of_carbon_monoxide_due_to_chemical_destruction',
                  'prodhcho':'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_chemical_production',
                  'losshcho':'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_chemical_destruction',
                  'losshchophoto':'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_chemical_destruction_by_photolysis',
                  'prodmethanol': 'tendency_of_atmosphere_mass_content_of_methanol_due_to_chemical_production',
                  'lossmethanol': 'tendency_of_atmosphere_mass_content_of_methanol_due_to_chemical_destruction',
                  #'lossisoprene':'tendency_of_atmosphere_mass_content_of_isoprene_due_to_chemical_destruction',
                  'prodh2o':'tendency_of_stratosphere_mass_content_of_water_vapor_due_to_chemical_production',
                  'lossh2o':'tendency_of_stratosphere_mass_content_of_water_vapor_due_to_chemical_destruction'}
                  

complist_ctm_dict = {'o3'       : 'O3',
                     'h2o'	: 'H2O',
                     'h2'	: 'H2',
                     'ch4'	: 'CH4',
                     'co'	: 'CO',
                     'hcho'	: 'CH2O',
                     'methanol'	: 'CH3OH',
                     'isop'	: 'ISOPRENE'}

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
scen = 'CNTR_v2'
yr = 'YR1'

filepath = '/div/qbo/users/ragnhibs/AlternativeFuels/methanol/CTM3results/'+scen+'/'+yr+ '/'

metyear_list = [2009,2010]

for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    print(filepath)

    #Loop trough filenames
    for c,comp in enumerate(long_name_dict):
        
        variable_id = comp
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
        print(filename)

        prodloss = comp[0:4]
        print(prodloss)
        var = comp[4:]
        print(var)

        
        if var == 'hchophoto':
            variable = complist_ctm_dict['hcho'] +'_'+ prodloss.upper()
            nchem = 3 # ! CH2O + hv   -> H2 + CO   DBCH2O
        elif var == 'ch4':
            variable = complist_ctm_dict[var] +'_'+ prodloss.upper()
            nchem = 2 # only OH + CH4  -> CH3 + H2O
        else:
            #Total loss and total production is nchemdiag 0
            variable = complist_ctm_dict[var] +'_'+ prodloss.upper()
            nchem = 0
                       
        print(variable)

        
        pl_data = read_prod_loss(filepath, year, year_out,variable)
       
        pl_data = pl_data.isel(nchemdiag=nchem)
       
        
        volume = read_avgsav_volume(filepath, year,year_out)
        print(volume)
        if c == 0:
            volume.to_netcdf('volume_' +time_range+'.nc' ,encoding={"time":{'dtype': 'float64'}})

        
        #If total production, we have to remove the emissions.
        if prodloss == 'prod' and var != 'h2o':
            emisdata = read_emis_accumulated(filepath,year,year_out,var,complist_ctm_dict[var])
            print(emisdata)
            pl_data[variable] = pl_data[variable] - emisdata[var]
            
            
        #Divide by volume
                
        pl_data[comp] = pl_data[variable]/volume['volume']
        pl_data[comp].attrs["unit"] =  'kg s-1 m-2'

                   
                
        data_out = pl_data[[comp]]
        data_out.attrs = pl_data.attrs
        data_out.attrs["history"] = history_text
        data_out[comp].attrs['long_name'] = long_name_dict[comp]

        
    
        print(data_out)

        print('Write to file:')
        print(filename)
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
      


