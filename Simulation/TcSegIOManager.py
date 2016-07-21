'''
READ ME:

When moving the model from one file system to another, change the
identity parameter. If the input and output directories are not present,
add them as shown in the IOManager class.

'''

import os

identity = 'Jeremy'

## DO NOT CHANGE THE FOLLOWING CODE!

class IOManager:
    def __init__(self):

        if identity == 'Jeremy':
            self.params_path = '~/Desktop/TC Model/Simulation/params.txt'
            self.stats_reporter_path = '~/Desktop/TC Model/tcseg_ParameterScan/'
            self.measurements_output_path = '~/Desktop/TC Model/tcseg_ParameterScan/'
        elif identity == 'Susan':
            self.params_path = '/Applications/CC3D_3.7.5_new/Simulations/tcseg/Simulation/params.txt'
            self.stats_reporter_path = '/Applications/CC3D_3.7.5_new/Simulations/tcseg/Stats_Output/'
            self.measurements_output_path = '/Applications/CC3D_3.7.5_new/Simulations/tcseg/Stats_Output/CSV_files/'

    def checkFileStructure(self):
        if not os.path.exists(self.params_path):
            raise NameError('No parameter file found! Please specify one in ElongationModel.py')
        if not os.path.exists(self.stats_reporter_path):
            print('No stats output path exists. Creating one at {}'.format(self.stats_reporter_path))
            os.makedirs(self.stats_reporter_path)
        if not os.path.exists(self.measurements_output_path):
            print('No result CSV file exists to output measurements! Creating one at', self.measurements_output_path)
            os.makedirs(self.measurements_output_path)
        
