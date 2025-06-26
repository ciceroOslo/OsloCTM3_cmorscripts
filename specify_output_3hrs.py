#Specify outputpath
outputpath = '/div/no-backup/users/ragnhibs/HYway/OsloCTM3output/final/3hrs/'

#Experiment and simulation information. To be used in the filename
table_id = '3hourly'
model_id = 'OsloCTM3v1-2'
#model_id = 'OsloCTM3v1-1'
experiment_id = 'transient2010s'
project_id = 'hyway'
member_id = 'r1'

#History text to be added to the file
history_text = 'OsloCTM3 simulations for HYway, contact: r.b.skeie@cicero.oslo.no'


year_use = 2015



if model_id == 'OsloCTM3v1-1':
    filepath = '/div/qbo/users/ragnhibs/HYway/CTM3results_wovocs/'
elif model_id == 'OsloCTM3v1-2':
    filepath = '/div/qbo/users/ragnhibs/HYway/CTM3results/'   





scen = str(year_use)
yr = ''



#List of meteorological year.
metyear_list = [year_use]
