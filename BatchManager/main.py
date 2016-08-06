from collections import OrderedDict
from BatchManagerScripts import ModelIOManager
from BatchManagerScripts import ResetBatch
from BatchManagerScripts import StepBackBatch
from BatchManagerScripts import ParamsPackager
from BatchManagerScripts import Convert2Video
from BatchManagerScripts import CompressVTKs
from BatchManagerScripts import InvokeCompuCell
from BatchManagerScripts import CreateSummary

# List the things that Manager can do.
options_dict = OrderedDict()
options_dict['Run batch'] = 'run_batch'
#options_dict['Reset and Run batch'] = 'reset_and_run_batch'
options_dict['Reset Simulation'] = 'reset'
#options_dict['Update ParameterScanSpecs.xml'] = 'update_parameter_scan_specs'
options_dict['Delete/redo the most recent simulation'] = 'step_back'
options_dict['Input File Locations'] = 'input_file_paths'
options_dict['Update File Locations in ElongationModel.py'] = 'sync'
options_dict['Convert current params.txt to .xml'] = 'convert_current_txt_file2xml'
options_dict['Convert another params.txt to .xml'] = 'convert_any_txt_file2xml'
options_dict['Create a summary of the batch runs'] = 'create_summary'
options_dict['Create a .mov from each runs\' .pngs'] = 'convert2vid'
options_dict['Compress VTK files'] = 'compress_vtks'
options_dict['Process ALL output'] = 'process_all'
#options_dict['Create summary.html] = 'create_summary'
#options_dict['Plot run data] = 'plot_run_data'


# Offer these options to the user, and invoke them when requested
def interface_loop(script_runner):
    print 'Options:'
    for i, option in enumerate(options_dict):
        print '\t({}) {}'.format(i, option)

    chosen_option_number = int(raw_input('Please input a number: Which program would you like to run? '))
    chosen_option_name = options_dict.keys()[chosen_option_number]
    chosen_option_func_name = options_dict[chosen_option_name]

    print '\nRunning: \'{}\'...\n'.format(chosen_option_name)

    result = getattr(script_runner, chosen_option_func_name)()

    print '\n'


# Class to invoke functions defined in subscripts
class managerSubscriptsCaller:
    def __init__(self):
        self.io_manager = ModelIOManager.IOManager(_silent=False)

    def convert_txt2xml(self, inpath):
        if inpath.endswith('.xml'):
            print 'The current params file is already an XML file'
        elif inpath.endswith('.txt'):
            dict = ParamsPackager.load_params_dict(inpath)
            xml_str = ParamsPackager.create_xml_from_params_dict(dict)
            ParamsPackager.write_xml_to_sim_directory(xml_str)
            user_input = raw_input('Do you want to use this xml file from now on? (Type \'yes\' to do so)')
            if user_input.lower() == 'yes':
                self.io_manager.params_path = self.io_manager.params_path.replace('.txt','.xml')
                self.io_manager.write_settings_XML_file()
        else:
            print 'The current params file is of unknown type. (File path = {}.) Aborting.'.format(inpath)

    def process_all(self):
        self.convert2vid()
        self.compress_vtks()
        # Clear old files

    def convert_any_txt_file2xml(self):
        path2xml = raw_input('Please input the location of the params.txt')
        self.convert_txt2xml(path2xml)

    def convert_current_txt_file2xml(self):
        path2xml = self.io_manager.params_path
        self.convert_txt2xml(path2xml)

    def run_batch(self):
        InvokeCompuCell.invoke_compucell()

    def reset_and_run_batch(self):
        self.reset()
        self.run_batch()

    def input_file_paths(self):
        self.io_manager.user_input_io_xml()

    def sync(self):
        self.io_manager.update_file_path_in_elongation_model_python()

    def reset(self):
        ResetBatch.reset()

    def step_back(self):
        StepBackBatch.step_back()
    
    def convert2vid(self):
        Convert2Video.convert_pngs_to_vid()

    def compress_vtks(self):
        CompressVTKs.compressVTKs()

    def update_parameter_scan_specs(self):
        ParamsPackager.update()

    def create_summary(self):
        CreateSummary.create_summary()



# Main interface loop
print 'Welcome to the Williams-Nagy Segmentation Model Manager (built by Jeremy Fisher)'
script_runner = managerSubscriptsCaller()
while True:
    interface_loop(script_runner)