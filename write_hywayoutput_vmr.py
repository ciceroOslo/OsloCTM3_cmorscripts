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
    tracer_file = 'input/tracer_list_all_h2_withVOC.d'
    header_list = ["TracerNumber","TCNAME","TCMASS","Comments"]
    df_tracer = pd.read_csv(tracer_file,skiprows=3,sep="\'",usecols=[0,1,2,3],names=header_list)

    molecw =df_tracer.loc[df_tracer['TCNAME'] == variable]['TCMASS'].values 

    return molecw




long_name_dict = {'ch3cooh':	'mole_fraction_of_acetic_acid_in_air',
                  'ch3coch3':	'mole_fraction_of_acetone_in_air',
                  'nh3':	'mole_fraction_of_ammonia_in_air',
                  'c6h6':	'mole_fraction_of_benzene_in_air',
                  'co':	        'mole_fraction_of_carbon_monoxide_in_air',
                  'dms':	'mole_fraction_of_dimethyl_sulfide_in_air',
                  'c2h6':	'mole_fraction_of_ethane_in_air',
                  'c2h4':	'mole_fraction_of_ethene_in_air',
                  'c2h2':	'mole_fraction_of_ethyne_in_air',
                  'hcho':	'mole_fraction_of_formaldehyde_in_air',
                  'hcooh':	'mole_fraction_of_formic_acid_in_air',
                  'chocho':	'mole_fraction_of_glyoxal_in_air',
                  'oh':	        'mole_fraction_of_hydroxyl_radical_in_air',
                  'isop':	'mole_fraction_of_isoprene_in_air',
                  'ch4':	'mole_fraction_of_methane_in_air',
                  'ch3oh':	'mole_fraction_of_methanol_in_air',
                  'mhp':	'mole_fraction_of_mhp_in_air',
                  'h2':	        'mole_fraction_of_molecular_hydrogen_in_air',
                  'mtp':	'mole_fraction_of_monoterpenes_in_air',
                  'hno3':	'mole_fraction_of_nitric_acid_in_air',
                  'no2':	'mole_fraction_of_nitrogen_dioxide_in_air',
                  'no':	        'mole_fraction_of_nitrogen_monoxide_in_air',
                  'nmvoc':	'mole_fraction_of_nmvoc_expressed_as_carbon_in_air',
                  'o3':	        'mole_fraction_of_ozone_in_air',
                  'pan':	'mole_fraction_of_peroxyacetyl_nitrate_in_air',
                  'c3h8':	'mole_fraction_of_propane_in_air',
                  'c3h6':	'mole_fraction_of_propene_in_air',
                  'so2':	'mole_fraction_of_sulfur_dioxide_in_air',
                  'tol':	'mole_fraction_of_toluene_in_air',
                  'h2o':	'mole_fraction_of_water_vapor_in_air'}



voclist = ['C2H4' ,#       28.052    'Ethene [CH2CH2]'
           'C2H6',#        30.068    'Ethane [CH3CH3]'
           'C3H6',#        42.078    'Propene [CH3CHCH2]'
           #'C4H10',#       58.120    'Butane [CH3CH2CH2CH3]' Added in the bigalk
           #'C6H14',#       86.188    'Dimethylbutane' Added in the bigalk
           'C6HXR_SOA',#  106.160    'm-Xylene/1,3-Dimethylbenzene [C8H10]'
           'CH2O'    ,#    30.026    'Formaldehyde'
           'CH3CHO' ,#     44.052    'Acetaldehyde'
           'CH3O2H' ,#     48.042    'Methyl hydroperoxide'
           'CH3COY' ,#     86.088    'Bi-acetyl [CH3COCOCH3]'
           'CH3COX' ,#     72.104    'Methylethyl ketone (2-butanone) [CH3COC2H5]'
           'ISOPRENE' ,#   68.114    'Isoprene/2-methylbuta-1,3-diene [C5H8]'
           'CH3COB',#     103.096    '[CH3COCH(O2)CH3]'
           'CH3XX' ,#      91.086    '[CH3CH(O2)CH2OH]'
           'AR1'  ,#      100.000    'Aromatic 1'
           'AR2'  ,#      100.000    'Aromatic 2'
           'AR3'  ,#      100.000    'Aromatic 3'
           'ISOR1',#      100.000    'Peroxy radicals (RO2) from ISOPREN'
           'ISOK' ,#      100.000    'methylvinylketone + methacrolein'
           'ISOR2' ,#     100.000    'Peroxy radicals from ISOK + OH'
           'HCOHCO',#      58.036    'Glyoxal'
           'RCOHCO' ,#     74.062    'Methyl glyoxal [CH3COCHO]'
           'CH3X'  ,#      75.044    'Peroxyacetyl radical [CH3COO2]'
           'C3H8'    ,#    44.094    'Propane'
           'C3H7O2' ,#     75.086    'Propyl peroxide; Radical from (propane+OH)+O2'
           'ACETONE',#     58.078    'Acetone [CH3COCH3]'
           'CH3COD'  ,#    89.070    'Propyldioxy, 2-oxo- [CH3COCH2(O2)], [C3H5O3]'
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
           'Trp_Ket',#    152.228    'Terpenoid ketone [C10H16O]
           'CH3O2'   ,#    47.034    ''
           'C2H5O2'  ,#    61.060    ''
           'C4H9O2' ,#     89.112    ''
           'C6H13O2', #    117.164    ''
           'SOAGAS11',
           'SOAGAS12',
           'SOAGAS13',
           'SOAGAS21',
           'SOAGAS22',
           'SOAGAS23',
           'SOAGAS31',
           'SOAGAS32',
           'SOAGAS33',
           'SOAGAS41',
           'SOAGAS42',
           'SOAGAS43',
           'SOAGAS51',
           'SOAGAS52',
           'SOAGAS53',
           'SOAGAS61',
           'SOAGAS62',
           'SOAGAS71',
           'SOAGAS72',
           'SOAGAS81',
           'SOAGAS82',
           'CH3COOH',#     60.052    'Acetic Acid'
           'C2H5OH',#      46.069    'Ethanol'
           'BIGALK',#      72.151    'Lumped Alkene C>3'
           'BIGENE',#      56.106    'Lumped Alkene C>3'
           'ALKO2',#       103.14    'Lumped alkane peroxy radical from BigAlk [C5H11O2]'
           'ALKOOH',#      104.15    'Lumped alkane hydroperoxide [C5H12O2]'
           'ALKNIT',#      117.15    'Standard Alkyl Nitrate from BIGALK + OH chem [C5H11ONO2]'
           'ENEO2',#       105.11    'Lumped hydroperoxy radical from OH + large alkenes [C4H9O3]'
           #'HONITR',#      135.12    'Lumped hydroxynitrates from various compounds [C4H9NO4]'
           'HCOOH',#       46.025    'Formic Acid'
           'C2H2']#        28.054    'Ethyne'



complist_ctm_dict = {'o3'       : ['O3'],
                     'h2o'	: ['H2O'],
                     'h2'	: ['H2'],
                     'ch4'	: ['CH4'],
                     'co'	: ['CO'],
                     'no2'	: ['NO2'],
                     'no'	: ['NO'],
                     'oh'	: ['OH'],
                     'hcho'	: ['CH2O'],
                     'so2'	: ['SO2'],
                     'c2h2'	: ['C2H2'],
                     'c2h4'	: ['C2H4'],
                     'c2h6'	: ['C2H6'],
                     'c3h6'	: ['C3H6'],
                     'c3h8'	: ['C3H8'],
                     'ch3coch3' : ['ACETONE'],
                     'ch3cooh'	: ['CH3COOH'],
                     'ch3oh'	: ['CH3OH'],
                     'dms'	: ['DMS'] ,
                     'hcooh'	: ['HCOOH'],
                     'hno3'	: ['HNO3'] ,
                     'isop'	: ['ISOPRENE'],
                     'mhp'	: ['CH3O2H'],
                     'mtp'	: ['Apine','Bpine','Limon','Myrcene','Sabine','D3carene', 'Ocimene', 'Trpolene', 'Trpinene'],
                     'nh3'	: ['NH3'],
                     'nmvoc'    : voclist,
                     'c6h6'     : ['Benzene'],
                     'tol'      : ['Tolmatic'], 
                     'pan'      : ['PANX','CH3X']}



filepath = filepath + scen+'/'+yr+ '/'


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
                data_field = calc_vmr(data_field,var,comp)
                print(data_field)
            else:
                print(var)
                data_field = calc_vmr(data_field,var,'tmp')
                if comp == 'pan':
                    data_field[comp] = data_field[comp] - data_field['tmp']
                else:
                    data_field[comp] = data_field[comp] + data_field['tmp']
                print(data_field)
                data_field = data_field.drop_vars('tmp')
                
        data_out = data_field[['ihya','ihyb',comp]]
        data_out.attrs = data_field.attrs
        data_out.attrs["history"] = history_text
        data_out.attrs["model_version"] = model_id
        data_out.attrs["file_created"] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        data_out[comp].attrs['long_name'] = long_name_dict[comp]

        if comp == 'nmvoc':
            print('No spesicif molecular weight')
        else:
            data_out[comp].attrs['molecular_weight'] = str(find_molecw(variables[0]))
            
        if comp == 'pan':
            data_out[comp].attrs['original_components'] = 'Difference '+'_'.join(variables)
        else:
            data_out[comp].attrs['original_components'] = '_'.join(variables)
        
        print(data_out)

        print('Write to file:')
        print(filename)
        data_out.to_netcdf(filename,encoding={"time":{'dtype': 'float64'}})
        


