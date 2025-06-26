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

def read_3hrs(filepath,fileprefix, year,variables):
    #Read 3hry files and combine to one dataset with time variable

    #Specify variable list
    variable_list = ['lat','lon','lev','time'] +  variables
    print(filepath)
    
    #Read all monthly files, add time variable and merge
    for day in range(0,365):
        files = f"{fileprefix}{year}_{day+1:03}.nc"
        #print(files)
        print(filepath +'/'+fileprefix+'/' + files )
      
        if day == 0:
            data = xr.open_dataset(filepath +'/'+fileprefix+'/' + files ) # ,decode_cf=False,decode_times=False)
            data = data.get(variable_list)
            #print(data)
                        
        else:
            data_add = xr.open_dataset(filepath +'/'+fileprefix+'/' + files ) # ,decode_cf=False,decode_times=False)
            #print(data_add)
            data_add = data_add.get(variable_list)
            #data_add = data_add.expand_dims(time=[datetime.datetime(year_out,mnd+1,15)])
            data = data.merge(data_add)
            #print(data)
           

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
    if variable == 'MNT':
        variable='Apine'
    #Find molecular weight for given variable

    #Read input file used in the CTM
    tracer_file = 'input/tracer_list_all_h2_withVOC.d'
    header_list = ["TracerNumber","TCNAME","TCMASS","Comments"]
    df_tracer = pd.read_csv(tracer_file,skiprows=3,sep="\'",usecols=[0,1,2,3],names=header_list)

    molecw =df_tracer.loc[df_tracer['TCNAME'] == variable]['TCMASS'].values 

    return molecw


long_name_dict = {'o3':'mole_fraction_of_ozone_in_air',
                  'co':'mole_fraction_of_carbon_monoxide_in_air',
                  'h2':'mole_fraction_of_molecular_hydrogen_in_air',
                  'ch4':'mole_fraction_of_methane_in_air',
                  'hcho':'mole_fraction_of_formaldehyde_in_air',
                  'h2o':'mole_fraction_of_water_vapor_in_air',
                  'nh3':'mole_fraction_of_ammonia_in_air',
                  'no':'mole_fraction_of_nitric oxide_in_air',
                  'no2':'mole_fraction_of_nitrogen_dioxide_in_air',
                  'hno3':'mole_fraction_of_nitric_acid_in_air',
                  'pan':'mole_fraction_of_peroxyacetlynitrate_in_air',
                  'ch3coch3':'mole_fraction_of_acetone_in_air',
                  'ch3cooh':'mole_fraction_of_acetic_acid_in_air',
                  'c2h6':'mole_fraction_of_ethane_in_air',
                  'c2h4':'mole_fraction_of_ethene_in_air',
                  'c2h2':'mole_fraction_of_ethyne_in_air',
                  'hcooh':'mole_fraction_of_formic_acid_in_air',
                  'ch3oh':'mole_fraction_of_methanol_in_air',
                  'mtp':'mole_fraction_of_monoterpenes_in_air',
                  'c3h6':'mole_fraction_of_propene_in_air',
                  'c3h8':'mole_fraction_of_propane_in_air',
                  'isop':'mole_fraction_of_isoprene_in_air',
                  'ch3cho': 'mole_fraction_of_acetaldehyde_in_air',
                  'c6h6':'mole_fraction_of_benzene_in_air',
                  'chocho':'mole_fraction_of_glyoxal_in_air'}






complist_ctm_dict = {'o3':['O3'],
                     'co':['CO'],
                     #'h2':['H2'],
                     #'ch4':['CH4'],
                     'hcho':['CH2O'],
                     'h2o': ['H2O'],
                     'nh3':['NH3'],
                     'no':['NO'],
                     'no2':['NO2'],
                     'hno3':['HNO3'] ,
                     'pan':['PANX','CH3X'],
                     'ch3coch3':['ACETONE'],
                     'ch3cooh': ['CH3COOH'],
                     'c2h6':['C2H6'],
                     'c2h4':['C2H4'],
                     #'c2h2':['C2H2'], Not included
                     'hcooh':['HCOOH'],
                     'ch3oh':['CH3OH'],
                     'mtp': ['MNT'],
                     'c3h6': ['C3H6'],
                     'c3h8':['C3H8'],
                     'isop':['ISOPRENE'],
                     'ch3cho': ['CH3CHO'],
                     'c6h6': ['Benzene'],
                     'chocho': ['HCOHCO']}

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

        
        variables = complist_ctm_dict[comp]

        print(len(variables))
        
        print(variables)

        if comp == 'mtp':
            fileprefix = 'mtr'
        else:
            fileprefix = 'trp'

        data_field=read_3hrs(filepath,fileprefix,year,variables)

        print(data_field)

        if len(variables) == 1:
            var = variables[0]
            print(var)
            molecw = find_molecw(var)
            print(molecw)

            data_field[comp] = data_field[var]*28.97/molecw
            data_field[comp].attrs['units'] = 'mol mol-1'

        else:
            if comp == 'pan':
                print('Do something here')
                var = variables[0]
                molecw = find_molecw(var)
                data_field[comp] = (data_field[variables[0]]-data_field[variables[1]])*28.97/molecw
                data_field[comp].attrs['units'] = 'mol mol-1'
                
            else:
                print('should not be here')
                
                
                        
        data_out = data_field[[comp]]
        data_out.attrs = data_field.attrs
        data_out.attrs["history"] = history_text
        data_out.attrs["model_version"] = model_id
        data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        data_out[comp].attrs['long_name'] = long_name_dict[comp]

        if comp == 'pan':
            data_out[comp].attrs['original_components'] = 'Difference '+'_'.join(variables)
        
        
        print(data_out)

        print('Write to file:')
        print(filename)
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
        


