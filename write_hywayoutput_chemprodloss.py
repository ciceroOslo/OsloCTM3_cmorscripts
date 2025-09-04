import numpy as np
import pandas as pd
import xarray as xr
import datetime
import sys

#This script read the OsloCTM3 model output and convert it to
#more standardized ouput. This script is adjusted to make the output
#in the format needed in HYway, but can easily be adjusted to other projects.

#In the specify_output.py file, set the different information regarding the model simulations that
#will be used.

from specify_output import *


#In addition to chemprod and loss, the script write also volume to netcdf file

#Check if variable is in the prod-loss output
def chech_if_pl_exist(filepath, year, year_out,variable):
    variable_list = ['lat','lon','lev','delta_time',variable]
    mnd = 0
    files = f"chemistryPL_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
    print(filepath + files)
        
    data = xr.open_dataset(filepath +'/' + files ,decode_cf=False,decode_times=False)
    isdata = True
    # Check if the variable 'your_variable' is in the dataset
    variable_name = 'your_variable'
    
    if variable in data.variables:
        print(f"Variable '{variable}' is present in the dataset.")
        isdata = True
    else:
        print(f"Variable '{variable}' is not present in the dataset.")
        isdata = False
        
    return isdata


#Read prodloss output
def read_prod_loss(filepath, year, year_out,variable):
    variable_list = ['lat','lon','lev','delta_time',variable]

    #print(variable_list)
   
    for mnd in range(0,12):
        files = f"chemistryPL_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
        #print(filepath + files)
        
        if mnd == 0:
            data = xr.open_dataset(filepath +'/' + files ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            data = data.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])

        else:
            data_add = xr.open_dataset(filepath +'/' + files ,decode_cf=False,decode_times=False)
            data_add = data_add.get(variable_list)
            data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)

    data.lat.attrs['long_name'] = 'latitude'
    data.lon.attrs['long_name'] = 'longitude'
    
    #NB delta_time in the OsloCTM3 output is wrong. Recalculate it here.
    days_in_month = data.time.dt.days_in_month
    data['delta_time'] = days_in_month*60.0*60.0*24.0
              
    data[variable] = data[variable]/data['delta_time'] #kg per gridbox per sec.

    data[variable].attrs['unit'] = 'kg s-1'
    
    return data


#Check if variable is emitted
def chech_if_emis_exist(filepath,year,year_out,variable_out,variable):
    variable_list = ['lat','lon','lev','gridarea','delta_time', variable]
    mnd = 0
    files = f"emis_accumulated_3d_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
    data = xr.open_dataset(filepath +'/emissions/' + files ,decode_cf=False,decode_times=False)
                    
    isdata = True
        
    if variable in data.variables:
        print(f"Variable '{variable}' is emitted.")
        isdata = True
    else:
        print(f"Variable '{variable}' is not emitted.")
        isdata = False
        
    return isdata


#Read emissions. Must be subtracted from the total production.
def read_emis_accumulated(filepath,year,year_out,variable_out,variable):
    variable_list = ['lat','lon','lev','gridarea','delta_time', variable]
    for mnd in range(0,12):
        files = f"emis_accumulated_3d_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
        #print(files)
        if mnd == 0:
            data = xr.open_dataset(filepath +'/emissions/' + files ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            data = data.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
        else:
            #print(mnd)
            data_add = xr.open_dataset(filepath +'/emissions/' + files ,decode_cf=False,decode_times=False)
            data_add = data_add.get(variable_list)
            data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)

    data.lat.attrs['long_name'] = 'latitude'
    data.lon.attrs['long_name'] = 'longitude'

    #NB delta_time in the OsloCTM3 output is wrong. Recalculate it here.
    days_in_month = data.time.dt.days_in_month
    data['delta_time'] = days_in_month*60.0*60.0*24.0
              
    #Keep in 3D
    data[variable_out] = data[variable]/data['delta_time']
    data[variable_out].attrs['unit'] = 'kg s-1'
    data = data.drop(variable)
          
    
    return data

#Read volume
def read_avgsav_volume(filepath, year,year_out):
    #Read avsavg monthly files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','ihya','ihyb','volume']

    #Read all monthly files, add time variable and merge
    for mnd in range(0,12):
        files = f"avgsav_{year}{mnd+1:02}01_{year+ (mnd+1)//12}{(mnd+1)%12+1:02}01.nc"
        if mnd == 0:
            data = xr.open_dataset(filepath +'/monthly_means/' + files ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            data = data.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
        else:
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


#long_name_dict = {#'prodo3':'tendency_of_atmosphere_mass_content_of_ozone_due_to_chemical_production',
#'losso3':'tendency_of_atmosphere_mass_content_of_ozone_due_to_chemical_destruction',

long_name_dict = {'prodh2':'tendency_of_atmosphere_mass_content_of_molecular_hydrogen_due_to_chemical_production',
                  'lossh2':'tendency_of_atmosphere_mass_content_of_molecular_hydrogen_due_to_chemical_destruction',
                  'lossch4':'tendency_of_atmosphere_mass_content_of_methane_due_to_chemical_destruction_by_hydroxyl_radical',
                  'prodco':'tendency_of_atmosphere_mass_content_of_carbon_monoxide_due_to_chemical_production',
                  'lossco':'tendency_of_atmosphere_mass_content_of_carbon_monoxide_due_to_chemical_destruction',
                  'prodhcho':'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_chemical_production',
                  'losshcho':'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_chemical_destruction',
                  'lossphotohcho':'tendency_of_atmosphere_mass_content_of_formaldehyde_due_to_chemical_destruction_by_photolysis',
                  'prodch3oh': 'tendency_of_atmosphere_mass_content_of_methanol_due_to_chemical_production',
                  'lossch3oh': 'tendency_of_atmosphere_mass_content_of_methanol_due_to_chemical_destruction',
                  'lossisop':'tendency_of_atmosphere_mass_content_of_isoprene_due_to_chemical_destruction',
                  'prodh2o':'tendency_of_stratosphere_mass_content_of_water_vapor_due_to_chemical_production',
                  'lossh2o':'tendency_of_stratosphere_mass_content_of_water_vapor_due_to_chemical_destruction',
                  'prodmhp':'tendency_of_atmosphere_mass_content_of_methyl_hydroperoxide_due_to_chemical_production',
                  'lossmhp':'tendency_of_atmosphere_mass_content_of_methyl_hydroperoxide_due_to_chemical_destruction',
                  'prodch3coch3': 'tendency_of_atmosphere_mass_content_of_acetone_due_to_chemical_production',
                  'lossch3coch3': 'tendency_of_atmosphere_mass_content_of_acetone_due_to_chemical_destruction',
                  'prodpan':'tendency_of_atmosphere_mass_content_of_peroxyacetyl_nitrate_due_to_chemical_production',
                  'losspan':'tendency_of_atmosphere_mass_content_of_peroxyacetyl_nitrate_due_to_chemical_destruction',
                  'lossc2h6':'tendency_of_atmosphere_mass_content_of_ethane_due_to_chemical_destruction',
                  'lossc2h4':'tendency_of_atmosphere_mass_content_of_ethene_due_to_chemical_destruction',
                  'prodchocho': 'tendency_of_atmosphere_mass_content_of_glyoxal_due_to_chemical_production',
                  'losschocho': 'tendency_of_atmosphere_mass_content_of_glyoxal_due_to_chemical_destruction',
                  'prodch3cooh': 'tendency_of_atmosphere_mass_content_of_acetic_acid_due_to_chemical_production',
                  'lossch3cooh': 'tendency_of_atmosphere_mass_content_of_acetic_acid_due_to_chemical_destruction',
                  'prodhcooh': 'tendency_of_atmosphere_mass_content_of_formic_acid_due_to_chemical_production',
                  'losshcooh': 'tendency_of_atmosphere_mass_content_of_formic_acid_due_to_chemical_destruction',
                  'prodphotoh2': 'tendency_of_atmosphere_mass_content_of_molecular_hydrogen_due_to_chemical_production',
                  'prodch3cho': 'tendency_of_atmosphere_mass_content_of_acetaldehyde_due_to_chemical_production',
                  'lossch3cho': 'tendency_of_atmosphere_mass_content_of_acetaldehyde_due_to_chemical_destruction',
                  'lossc6h6': 'tendency_of_atmosphere_mass_content_of_benzene_due_to_chemical_destruction',
                  'lossc2h2':'tendency_of_atmosphere_mass_content_of_ethyne_due_to_chemical_destruction'}


complist_ctm_dict = {'o3'       : 'O3', 
                     'h2o'	: 'H2O', 
                     'h2'	: 'H2', 
                     'ch4'	: 'CH4', 
                     'co'	: 'CO',
                     'hcho'	: 'CH2O',
                     'ch3oh'	: 'CH3OH', 
                     'isop'	: 'ISOPRENE',
                     'mhp'      : 'CH3O2H',
                     'ch3coch3' : 'ACETONE', 
                     'chocho'   : 'HCOHCO',
                     'pan'      : 'PANX',
                     'c2h6'     : 'C2H6',
                     'c2h4'     : 'C2H4',
                     'c2h2'     : 'C2H2',
                     'hcooh'    : 'HCOOH',
                     'ch3cooh'  : 'CH3COOH',
                     'c6h6'     : 'Benzene',
                     'ch3cho'   : 'CH3CHO'} 

filepath = filepath +scen+'/'+yr+ '/'

for m,metyear in enumerate(metyear_list):

    print(metyear)
    #For steady state simulations, have to make changes here.
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    print(filepath)

    #Loop trough filenames
    for c,comp in enumerate(long_name_dict):
        print(comp)
        variable_id = comp
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'


        prodloss = comp[0:4]
        var = comp[4:]

        if var == 'photohcho':
            variable = complist_ctm_dict['hcho'] +'_'+ prodloss.upper()
            nchem = -99
            nchem_list = [2, 3] # ! CH2O + hv   -> H2 + CO   DBCH2O
           
            #CHEMLOSS(3,13,L) = CHEMLOSS(3,13,L) + DACH2O*M_CH2O*DTCH
            #CHEMLOSS(4,13,L) = CHEMLOSS(4,13,L) + DBCH2O*M_CH2O*DTCH
            
        elif var == 'photoh2':
            variable = complist_ctm_dict['h2'] +'_'+ prodloss.upper()
            nchem = 1 #  ! CH2O + hv   -> H2 + CO   DBCH2O
        elif var == 'ch4':
            variable = complist_ctm_dict[var] +'_'+ prodloss.upper()
            nchem = 2 # only OH + CH4  -> CH3 + H2O
        else:
            #Total loss and total production is nchemdiag 0
            variable = complist_ctm_dict[var] +'_'+ prodloss.upper()
            nchem = 0
                       

        #Check if data:
        isdata = chech_if_pl_exist(filepath, year, year_out,variable)
        
        if isdata:
            pl_data = read_prod_loss(filepath, year, year_out,variable)

            if prodloss == 'loss' and nchem == 0:
                #Remove drydeposition from total chemical production
                pl_data = pl_data.isel(nchemdiag=nchem)-pl_data.isel(nchemdiag=1)
            elif nchem == -99 : # photohcho
                pl_data = pl_data.isel(nchemdiag=nchem_list[0])+pl_data.isel(nchemdiag=nchem_list[1])
                
            else:
                pl_data = pl_data.isel(nchemdiag=nchem)
        
            volume = read_avgsav_volume(filepath, year,year_out)

            #Write volume to file 
            if c == 0:
                volume_filename = outputpath + 'volume' +'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
                print('Write to file: ' + volume_filename)
                volume.to_netcdf(volume_filename ,encoding={"time":{'dtype': 'float64'}})


                
        
            #If total production, we have to remove the emissions.
            if (prodloss == 'prod'):
                if(var == 'photoh2'): #Can also check if nchem = 0.
                    is_emitted = False
                else:
                    is_emitted = chech_if_emis_exist(filepath,year,year_out,var,complist_ctm_dict[var])
                    
                if(is_emitted):
                    emisdata = read_emis_accumulated(filepath,year,year_out,var,complist_ctm_dict[var])
                    pl_data[variable] = pl_data[variable] - emisdata[var]
                    
        
            #Divide by volume
                
            pl_data[comp] = pl_data[variable]/volume['volume']
            pl_data[comp].attrs["unit"] =  'kg m-3 s-1'

                   
                
            data_out = pl_data[[comp]]
            data_out.attrs = pl_data.attrs
            data_out.attrs["history"] = history_text
            data_out[comp].attrs['long_name'] = long_name_dict[comp]

            print('Write to file:')
            print(filename)
            data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
        else:
            print('NO DATA ' + variable)


