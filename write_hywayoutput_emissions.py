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
              
        
    data[variable_out] = data[variable].sum(dim='lev')/(data['gridarea']*data['delta_time'])
    data[variable_out].attrs['unit'] = 'kg m-2 s-1'
    
          
    
    return data


long_name_dict = {'emich3cho':'Total emission rate of acetaldehyde',
                  'emic6h6':'Total emission rate of benzene',
                  'emich3cooh':'Total emission rate of acetic acid',
                  'emich3coch3':'Total emission rate of acetone',
                  'eminh3':'Total emission rate of ammonia',
                  'emico':'Total emission rate of carbon monoxide',
                  'emidms':'Total emission rate of dimethyl sulfide',	
                  'emic2h2':'Total emission rate of ethyne',
	          'emic2h4':'Total emission rate of ethene',	
	          'emic2h6':'Total emission rate of ethane',
                  'emihcho':'Total emission rate of formaldehyde',
                  'emihcooh':'Total emission rate of formic acid',
                  'emiisop':'Total emission rate of isoprene',
                  'emich4':'Total emission rate of methane',
                  'emich3oh':'Total emission rate of methanol',
                  'emih2':'Total emission rate of hydrogen',
	          'emimtp':'Total emission rate of monoterpenes',
                  'emitotno': 'Total emission rate of no',
                  'emino2': 'Total emission rate of no2',
                  'eminmvoc':'Total emission rate of nmvoc',	
	          'emic3h6':'Total emission rate of propene',	
	          'emic3h8':'Total emission rate of propane',	
	          'emiso2':'Total emission rate of sulfur dioxide',	
	          'emiso4':'Total direct emission rate of sulphate'}	



voclist = ['C2H4' ,#       28.052    'Ethene [CH2CH2]'
           'C2H6',#        30.068    'Ethane [CH3CH3]'
           'C3H6',#        42.078    'Propene [CH3CHCH2]'
           'C4H10',#       58.120    'Butane [CH3CH2CH2CH3]'
           'C6H14',#       86.188    'Dimethylbutane'
           'C6HXR_SOA',#  106.160    'm-Xylene/1,3-Dimethylbenzene [C8H10]'
           'CH2O'    ,#    30.026    'Formaldehyde'
           'CH3CHO' ,#     44.052    'Acetaldehyde'
           #'CH3O2H' ,#     48.042    'Methyl hydroperoxide'
           #'CH3COY' ,#     86.088    'Bi-acetyl [CH3COCOCH3]'
           #'CH3COX' ,#     72.104    'Methylethyl ketone (2-butanone) [CH3COC2H5]'
           'ISOPRENE' ,#   68.114    'Isoprene/2-methylbuta-1,3-diene [C5H8]'
           #'CH3COB',#     103.096    '[CH3COCH(O2)CH3]'
           #'CH3XX' ,#      91.086    '[CH3CH(O2)CH2OH]'
           #'AR1'  ,#      100.000    'Aromatic 1'
           #'AR2'  ,#      100.000    'Aromatic 2'
           #'AR3'  ,#      100.000    'Aromatic 3'
           #'ISOR1',#      100.000    'Peroxy radicals (RO2) from ISOPREN'
           #'ISOK' ,#      100.000    'methylvinylketone + methacrolein'
           #'ISOR2' ,#     100.000    'Peroxy radicals from ISOK + OH'
           #'HCOHCO',#      58.036    'Glyoxal'
           #'RCOHCO' ,#     74.062    'Methyl glyoxal [CH3COCHO]'
           #'CH3X'  ,#      75.044    'Peroxyacetyl radical [CH3COO2]'
           #'C3H8'    ,#    44.094    'Propane'
           #'C3H7O2' ,#     75.086    'Propyl peroxide; Radical from (propane+OH)+O2'
           'ACETONE',#     58.078    'Acetone [CH3COCH3]'
           #'CH3COD'  ,#    89.070    'Propyldioxy, 2-oxo- [CH3COCH2(O2)], [C3H5O3]'
           'CH3OH'  ,#     32.032    'Methanol'
           'Tolmatic' ,#   92.134    'Toluene + ... [C7H8]'
           'Benzene',#     78.108    'Benzene [C6H6]'
           'Apine' ,#     136.228    'alpha-Pinene [C10H16]'
           'Bpine',#      136.228    'beta-Pinene [C10H16]'
           'Limon'  ,#    136.228    'limonene [C10H16]'
           'Myrcene' ,#   136.228    'myrcene [C10H16]'
           'Sabine'  ,#   136.228    'sabinene [C10H16]'
           'D3carene' ,#  136.228    '3-carene [C10H16]'
           'Ocimene'  ,#  136.228    'ocimene [C10H16]'
           'Trpolene',#   136.228    'Terpinolene, isoterpinene [C10H16]'
           'Trpinene' ,#  136.228    'Terpinene (alpha+gamma) [C10H16]'
           'TrpAlc' ,#    154.244    'Terpeoid alcohols [C10H18O]'
           'Sestrp' ,#    204.342    'Sesquiterpenes [C15H24]'
           'Trp_Ket', #    152.228    'Terpenoid ketone [C10H16O]
           'C2H2',
           'CH3COOH',
           'HCOOH',
           'BIGENE',
           'C2H5OH']

           
complist_dict = {'emich3cho':['CH3CHO'],
                 'emic6h6':['Benzene'],
                 'emic2h4': ['C2H4'],
	         'emic2h6': ['C2H6'],
	         'emic3h6': ['C3H6'],
	         'emic3h8': ['C3H8'],
	         'emich3coch3':['ACETONE'],
	         'emich3oh': ['CH3OH'],
	         #'emich4': ['CH4'],
	         'emico': ['CO'],
	         'emidms': ['DMS'],
	         #'emih2': ['H2'],
	         'emihcho': ['CH2O'],
	         'emiisop': ['ISOPRENE'],
	         'emimtp': ['Apine','Bpine','Limon','Myrcene','Sabine','D3carene', 'Ocimene', 'Trpolene', 'Trpinene'],
	         'eminh3': ['NH3'],
	         'emitotno': ['NO'],
                 'emino2': ['NO2'],
	         'emiso2': ['SO2'],
	         'emiso4': ['SO4'],
                 'emich3cooh': ['CH3COOH'],
                 'emihcooh': ['HCOOH'],
                 'eminmvoc': voclist,
                 'emic2h2': ['C2H2']}


filepath = filepath + scen+'/'+yr+ '/'


for m,metyear in enumerate(metyear_list):
    #For steady state simulations, have to make changes here.
    year = metyear
    year_out  = year

    time_range = str(year)+ '01-' + str(year) + '12'

    write_to_file = False
    for comp in complist_dict:
        print(comp)
        variable_id = comp 
        filename = outputpath + variable_id+'_'+table_id+'_'+model_id+'_'+project_id + '_' +experiment_id+'_'+member_id+'_'+time_range+'.nc'
        
    
        for v, variable in enumerate(complist_dict[comp]):
            if v == 0:
                print(variable)

                isdata = chech_if_emis_exist(filepath,metyear,year_out,comp,variable)
                if isdata:
                    data_field = read_emis_accumulated(filepath,metyear,year_out,comp,variable)
                    write_to_file = True
                else:
                    write_to_file = False
            else:
                print(variable)
                isdata = chech_if_emis_exist(filepath,metyear,year_out,'tmp',variable)
                
                if isdata:
                    data = read_emis_accumulated(filepath,metyear,year_out,'tmp',variable)
                    data_field[comp] = data_field[comp] + data['tmp']
                    

        if write_to_file:        
            data_out = data_field[[comp]]
            data_out.attrs["history"] = history_text
            data_out.attrs["model_verison"] = model_id
            data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            
            data_out[comp].attrs['long_name'] = long_name_dict[comp]
            
                        
            print('Write to file:')
            print(filename)
            
            data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
      


