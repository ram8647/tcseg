import os
import platform
from tempfile import mkstemp
from shutil import move, rmtree
from fnmatch import fnmatch
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse
import xml.dom.minidom as minidom
from itertools import product
from collections import OrderedDict
import getpass

# File manipulation helper functions
def process_path(dir):
    if os.path.isdir(dir):
        if not dir.endswith('/'):
            dir += '/'
    return dir

def parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))

class IOManager:
    '''
    IOManager keeps track of file paths, reading them from an XML file or -- if it
    does exists -- creating one from autodetecting the file path or asking the
    user.
    '''
    def __init__(self, _silent = False):

        # Declare variables that store the filepaths...

        # ...these variables must be detected or inputted from the user directly
        self.model_path = ''
        self.params_path = ''
        self.output_folder = ''
        self.cc3d_command_dir = ''
        # ...whereas these variables are automatically constructed in self.autodetect_file_paths()
        self.parameter_scan_specs_xml_file_path = ''
        self.elongation_model_python_path = ''
        self.screenshot_output_path = ''
        self.simulation_folder_path = ''
        self.param_scan_command_dir = ''
        self.run_script_command_dir = ''
        self.apple_script_dir = ''

        # Declare other variables having to do with maintaining IOManager itself

        self.silent = _silent # Turning off silent makes the console output slightly more verbose
        self.cached_variable_number_of_runs = None # Stores the number of runs in a batch, if the proper batch files are present
        self.GUI_messages = [] # All the messages that the GUI should know about

        # Now, IOManager will try to figure out the file paths automatically
        self.autodetect_file_paths()

        # Hopefully, autodetect will work. Even if not, IOManager will try to read the paths from the settings XML file
        try:
            self.read_xml()
        # If there is no settings file, just print this to the console. We'll ask the user in a minute.
        except IOError:
            if not self.silent:
                print 'No setting file exists!'

        # For any file paths that IOManager could not figure out on its own, ask the user
        if self.params_path == '':
            self.GUI_messages.append('ask_for_params')
        if self.cc3d_command_dir == '':
            self.GUI_messages.append('ask_for_compucell_command')
        if self.output_folder == '':
            self.GUI_messages.append('ask_for_output_folder')
        if self.model_path == '':
            self.GUI_messages.append('ask_for_model_folder')

        # If everything has gone smoothly, and we have all the paths, find the rest of them
        if self.params_path != '' and self.cc3d_command_dir != '' and self.output_folder != '' and self.model_path != '':
            self.construct_additional_paths()

    def read_xml(self):
        '''
        Reads the settings from ModelIOManager_Settings_username.xml ; it will NOT override
        the paths that autodetect_file_paths() finds.
        '''

        username = getpass.getuser()
        settings_xml_path = os.path.join(os.getcwd(), 'ModelIOManager_Settings_{}.xml'.format(username))
        if not self.silent:
            print '\nReading remaining unknown file paths from: {}\n'.format(settings_xml_path)

        xml_file = parse(settings_xml_path)
        xml_root = xml_file.getroot()

        for child in xml_root:
            if child.tag == 'output_folder' and self.output_folder == '':
                self.output_folder = child.text
            if child.tag == 'params_path' and self.params_path == '':
                self.params_path = child.text
            if child.tag == 'cc3d_command_dir' and self.cc3d_command_dir == '':
                self.cc3d_command_dir = child.text
            if child.tag == 'model_path' and self.model_path == '':
                self.model_path = child.text

    def construct_additional_paths(self):
        '''
        Finds the paths that we can find automatically, without needing to ask the user directly.
        '''

        # Construct paths in /CC3D_3.7.5/
        compucell_parent_dir = parent_dir(self.cc3d_command_dir)
        self.param_scan_command_dir = os.path.join(compucell_parent_dir, 'paramScan.command')
        self.run_script_command_dir = os.path.join(compucell_parent_dir, 'runScript.command')

        # Construct paths in the Segmentation
        self.model_cc3d_file = os.path.join(self.model_path, 'tcseg_batch.cc3d')
        self.simulation_folder_path = os.path.join(self.model_path, 'Simulation')
        self.parameter_scan_specs_xml_file_path = os.path.join(self.model_path, 'Simulation/ParameterScanSpecs.xml')
        self.elongation_model_python_path = os.path.join(self.model_path, 'Simulation/ElongationModel.py')
        self.apple_script_dir = os.path.join(self.model_path, 'BatchManager/BatchManagerScripts/ForceRunCompuCell.scpt')

        # Construct path to the parameter scan folder, if it exists
        for dir_in_output_folder in os.listdir(self.output_folder):
            if fnmatch(dir_in_output_folder, '*_ParameterScan'):
                self.screenshot_output_path = os.path.join(self.output_folder, dir_in_output_folder)

        # If it doesnt exists, make one at tcseg_batch/Output/tcseg_ParameterScan
        if not os.path.isdir(self.screenshot_output_path):
            self.screenshot_output_path = os.path.join(self.output_folder, 'tcseg_ParameterScan')
            os.mkdir(self.screenshot_output_path)

    def update_file_path_in_elongation_model_python(self):
        '''
        Our model relies on knowing the absolute location of several external files. This function
        updates ElongationModel.py to those stored in IOManager's settings.

        Much of the following code goes through each line, looks for flags, and replaces certain lines
        with these absolute paths.
        '''

        model_file_path = self.elongation_model_python_path

        fh, abs_path = mkstemp()
        with open(abs_path, 'w') as new_elongation_model_file:
            with open(model_file_path, 'r') as old_elongation_model_file:
                for line in old_elongation_model_file:
                    try:
                        trailing_comment = line.split()[-1]
                        if trailing_comment == '#IO_MANAGER_FLAG_A_DO_NOT_CHANGE_THIS_COMMENT':
                            first_part_of_line = line.split('\'')[0]
                            new_line = '{}\'{}\' #IO_MANAGER_FLAG_A_DO_NOT_CHANGE_THIS_COMMENT\n'.format(first_part_of_line,self.params_path)
                            new_elongation_model_file.write(new_line)
                        elif trailing_comment == '#IO_MANAGER_FLAG_B_DO_NOT_CHANGE_THIS_COMMENT':
                            first_part_of_line = line.split('\'')[0]
                            new_line = '{}\'{}\' #IO_MANAGER_FLAG_B_DO_NOT_CHANGE_THIS_COMMENT\n'.format(first_part_of_line, self.output_folder)
                            new_elongation_model_file.write(new_line)
                        elif trailing_comment == '#IO_MANAGER_FLAG_C_DO_NOT_CHANGE_THIS_COMMENT':
                            first_part_of_line = line.split('\'')[0]
                            new_line = '{}\'{}\' #IO_MANAGER_FLAG_C_DO_NOT_CHANGE_THIS_COMMENT\n'.format(first_part_of_line, self.parameter_scan_specs_xml_file_path)
                            new_elongation_model_file.write(new_line)
                        else:
                            new_elongation_model_file.write(line)
                    except IndexError: # this will happen when we encounter a blank line
                        new_elongation_model_file.write(line)

        os.close(fh)
        os.remove(model_file_path) # Remove original file
        move(abs_path, model_file_path) # Move new file

    def write_settings_XML_file(self):
        '''
        Saves the file paths
        '''
        # Create the XML
        root = ET.Element('file_paths')
        model_path_element = ET.SubElement(root, 'model_path')
        model_path_element.text = self.model_path
        params_path_element = ET.SubElement(root, 'params_path')
        params_path_element.text = self.params_path
        output_folder_element = ET.SubElement(root, 'output_folder')
        output_folder_element.text = self.output_folder
        cc3d_command_dir_element = ET.SubElement(root, 'cc3d_command_dir')
        cc3d_command_dir_element.text = self.cc3d_command_dir

        # Write it out
        username = getpass.getuser()
        outpath = os.path.join(os.getcwd(), 'ModelIOManager_Settings_{}.xml'.format(username))
        rough_string = ET.tostring(root)
        reparsed = minidom.parseString(rough_string)
        pretty_str = reparsed.toprettyxml(indent="\t")
        with open(outpath, 'w') as settings_file:
            settings_file.write(pretty_str)

    def number_of_runs(self):
        '''
        Parse the xml dictionary for batch values and calculate how many times the simulation will have
        to run. However, if this function has run already, it will just return the cached value.
        :return: the number of runs that an xml file will cause
        '''
        def has_children(xml_element):
            return True if len(list(xml_element)) else False

        if not self.cached_variable_number_of_runs == None:
            return self.cached_variable_number_of_runs

        if not self.params_path.endswith('.xml'):
            return 1
        else:
            batch_vars_dict = OrderedDict()
            batch_id_to_param_name_table = OrderedDict()

            # Open params.xml
            xml_file = parse(self.params_path)
            xml_root = xml_file.getroot()

            # Generate a unique ID for each parameter that changes between runs, and link its name to its id in a table
            def assign_batch_id(_name):
                new_batch_id = 'batch_id_{}'.format(len(batch_vars_dict))
                batch_id_to_param_name_table[new_batch_id] = _name
                return new_batch_id

            for parameter_element in xml_root.iter('param'):
                if has_children(parameter_element):
                    batch_id = assign_batch_id(parameter_element.attrib['name'])
                    batch_vars_dict[batch_id] = []
                    for values_element in parameter_element.iter('BatchValue'):
                        batch_vars_dict[batch_id].append(0)

            # If there are no batch variables, then it will run once
            if len(batch_vars_dict.keys()) == 0:
                return 1

            # Otherwise, generate a list of tuples, each containing a unique combination of batch variables
            all_combinations_of_params = list(product(*[batch_vars_dict[key] for key in batch_vars_dict]))
            num_runs = len(all_combinations_of_params)
            return num_runs

    def move_all_files_to_output_folder(self):
        '''
        At the end of a batch runs, there will only be a few interesting files in the ParameterScan
        directory. This function moves them all to the Output folder.
        '''
        for root, dirs, files in os.walk(self.screenshot_output_path):
            for output_file in files:
                for interesting_file_type in ['*.zip','*.mov','*_3600.png']:
                    if fnmatch(output_file, interesting_file_type):
                        old_path = os.path.join(root, output_file)
                        new_path = os.path.join(self.output_folder, output_file)
                        move(old_path, new_path)

    def delete_unnecessary_output_files(self, check=False):
        '''
        Like move_all_files_to_output_folder(), this function removes uninteresting output
        from the ParameterScan directory. This keeps things clean.

        :param check: If check is true, the user must type 'yes' before deleting the old stuff
        '''
        if check == True:
            confirm = raw_input('Are you sure you want to delete unnecessary files? [type yes] ')
            if confirm.lower() != 'yes':
                return

        rmtree(self.screenshot_output_path)

    def autodetect_file_paths(self):
        '''
        main_UI.py should be executed in a certain place, such that the current working directory is
        a child of the parent of the model path. If so, IOManager will autodetect all the important
        file paths.

        :return: False if the function cannot find the correct files
        '''

        # First, look in the default directories for CompuCell
        if platform.system() == 'Linux':
            default_dir = '/usr/lib/compucell3d/compucell3d.sh'
            if os.path.isfile(default_dir):
                self.cc3d_command_dir = '/usr/lib/compucell3d/compucell3d.sh'
        if platform.system() == 'Darwin':
            for dir in os.listdir('/Applications'):
                if fnmatch(dir, 'CC3D_*'):
                    self.cc3d_command_dir = os.path.join('/Applications',dir,'compucell3d.command')

        cwd = os.getcwd()
        proposed_model_path = parent_dir(cwd)
        proposed_output_folder = process_path(os.path.join(proposed_model_path, 'Output'))

        if not self.silent:
            print '\nCurrent Working Directory: {}\n'.format(cwd)

        if not self.silent:
            print '\tOpening {} at {}'.format('Model Path', proposed_model_path)
        if os.path.isdir(proposed_model_path):
            self.model_path = process_path(proposed_model_path)
            if not self.silent:
                print '\t->Seems legit. Continuing...'
        else:
            print '\tFailed to open model path!\n'
            self.user_input_io_xml()
            return False

        if not self.silent:
            print '\tOpening {} at {}'.format('Output Path', proposed_output_folder)
        if os.path.isdir(proposed_output_folder):
            self.output_folder = process_path(proposed_output_folder)
            if not self.silent:
                print '\t->Seems legit. Continuing...'
        else:
            print '\tFailed to open output path!\n'
            return False

    def open_a_params_file(self, path):
        '''
        :param path: path to new params file
        '''
        new_params_path = ''
        if path.endswith('.txt') or path.endswith('.xml'):
            self.params_path = new_params_path
            self.write_settings_XML_file()
            self.update_file_path_in_elongation_model_python()


