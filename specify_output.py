#Specify outputpath
outputpath = '/div/no-backup/users/ragnhibs/HYway/OsloCTM3output/SIM4/'

#Experiment and simulation information. To be used in the filename
table_id = 'monthly'
model_id = 'OsloCTM3v1-2'

experiment_id = 'cntr1850'
#experiment_id = 'h2antr1850'

project_id = 'hyway'
member_id = 'r1'

#History text to be added to the file
history_text = 'OsloCTM3 simulations for HYway, contact: r.b.skeie@cicero.oslo.no'


#year_use = 2019 #2013


filepath = '/div/qbo/users/ragnhibs/HYway/CTM3results_sim4/'

scen_list = {'cntr1850':'cntr1850',
             'h2antr1850':'h2antr1850'}
    
scen = scen_list[experiment_id]
yr = 'YR1'

yrstart = 2019 + int(yr[2:])*2-1
print(yrstart)

#List of meteorological year.
metyear_list = [2018,2019]
