#Specify outputpath
outputpath = '/div/no-backup/users/ragnhibs/HYway/OsloCTM3output/'

#Experiment and simulation information. To be used in the filename
table_id = 'monthly'
model_id = 'OsloCTM3v1.2'
#model_id = 'OsloCTM3v1.1'
experiment_id = 'transient2010s'
project_id = 'hyway'
member_id = 'r1'

#History text to be added to the file
history_text = 'OsloCTM3 simulations for HYway, contact: r.b.skeie@cicero.oslo.no'

#Raw model output information
#filepath = filepath +scen+'/'+yr+ '/'

#filepath =  '/div/qbo/users/srkri/'
#scen = 'VOC-OsloCTM3/CTM3_hyway_test2010.070425.72834'
#yr = ''


if model_id == 'OsloCTM3v1.1':
    filepath = '/div/qbo/users/ragnhibs/HYway/CTM3results_wovocs/'
elif model_id == 'OsloCTM3v1.2':
    filepath = '/div/qbo/users/ragnhibs/HYway/CTM3results/'   


scen = '2015'
yr = ''

#
#scen = '2010'
#yr = ''

#List of meteorological year.
metyear_list = [2015]
