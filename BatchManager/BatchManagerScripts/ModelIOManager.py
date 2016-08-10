from collections import OrderedDict
from tempfile import mkstemp
import os
from os import remove, close
from shutil import move, rmtree
from fnmatch import fnmatch
from itertools import product
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, parse
import getpass
import xml.dom.minidom as minidom

# Todo: Add error when the user specifies a clearly wrong directory or file

class IOManager:
    def __init__(self, _silent = True):
        self.silent = _silent
        self.model_path = ''
        self.params_path = ''
        self.output_folder = ''
        self.cc3d_command_dir = ''
        self.parameter_scan_specs_xml_file_path = ''
        self.elongation_model_python_path = ''
        self.screenshot_output_path = ''
        self.simulation_folder_path = ''
        self.param_scan_command_dir = ''
        self.run_script_command_dir = ''
        self.cached_variable_number_of_runs = None

        self.GUI_messages = []

        # Try to figure out the file paths
        self.autodetect_file_paths()
        try:
            self.read_xml()
        except IOError:
            print 'No setting file exists!'
            self.GUI_messages.append('ask_for_params')
            self.GUI_messages.append('ask_for_compucell_command')

    def user_input_io_xml(self):
        # Have the user input the file paths
        if self.model_path == '':
            self.model_path = process_path(raw_input('Where is folder containing tcseg_batch.cc3d? '))
        if self.params_path == '':
            self.params_path = process_path(raw_input('Where is params.txt (or params.xml)? '))
        if self.output_folder == '':
            self.output_folder = process_path(raw_input('Where do you want to keep output PNGs and VTKs? '))
        if self.cc3d_command_dir == '':
            self.cc3d_command_dir = process_path(raw_input('Where is compucell3d.command? '))

        self.construct_additional_paths()

    def read_xml(self):
        username = getpass.getuser()
        inpath = os.path.join(os.getcwd(), 'ModelIOManager_Settings_{}.xml'.format(username))

        if not self.silent:
            print '\nReading remaining unknown file paths from: {}\n'.format(inpath)
        xml_file = parse(inpath)
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

        self.construct_additional_paths()

    def construct_additional_paths(self):
        compucell_parent_dir = os.path.abspath(os.path.join(self.cc3d_command_dir, os.pardir))
        self.param_scan_command_dir = os.path.join(compucell_parent_dir, 'paramScan.command')
        self.run_script_command_dir = os.path.join(compucell_parent_dir, 'runScript.command')
        self.model_cc3d_file = os.path.join(self.model_path, 'tcseg_batch.cc3d')
        self.simulation_folder_path = os.path.join(self.model_path, 'Simulation')
        self.parameter_scan_specs_xml_file_path = os.path.join(self.model_path, 'Simulation/ParameterScanSpecs.xml')
        self.elongation_model_python_path = os.path.join(self.model_path, 'Simulation/ElongationModel.py')

        for dir_in_output_folder in os.listdir(self.output_folder):
            if fnmatch(dir_in_output_folder, '*_ParameterScan'):
                self.screenshot_output_path = os.path.join(self.output_folder, dir_in_output_folder)

        if not os.path.isdir(self.screenshot_output_path):
            self.screenshot_output_path = os.path.join(self.output_folder, 'tcseg_ParameterScan')

    def update_file_path_in_elongation_model_python(self):
        file_path = self.elongation_model_python_path

        fh, abs_path = mkstemp()
        with open(abs_path, 'w') as new_file:
            with open(file_path, 'r') as old_file:
                for line in old_file:
                    try:
                        trailing_comment = line.split()[-1]
                        if trailing_comment == '#IO_MANAGER_FLAG_A_DO_NOT_CHANGE_THIS_COMMENT':
                            first_part_of_line = line.split('\'')[0]
                            new_line = '{}\'{}\' #IO_MANAGER_FLAG_A_DO_NOT_CHANGE_THIS_COMMENT\n'.format(first_part_of_line,self.params_path)
                            new_file.write(new_line)
                        elif trailing_comment == '#IO_MANAGER_FLAG_B_DO_NOT_CHANGE_THIS_COMMENT':
                            first_part_of_line = line.split('\'')[0]
                            new_line = '{}\'{}\' #IO_MANAGER_FLAG_B_DO_NOT_CHANGE_THIS_COMMENT\n'.format(first_part_of_line, self.output_folder)
                            new_file.write(new_line)
                        elif trailing_comment == '#IO_MANAGER_FLAG_C_DO_NOT_CHANGE_THIS_COMMENT':
                            first_part_of_line = line.split('\'')[0]
                            new_line = '{}\'{}\' #IO_MANAGER_FLAG_C_DO_NOT_CHANGE_THIS_COMMENT\n'.format(first_part_of_line, self.parameter_scan_specs_xml_file_path)
                            new_file.write(new_line)
                        else:
                            new_file.write(line)
                    except IndexError: # this will happen when we encounter a blank line
                        new_file.write(line)

        close(fh)
        remove(file_path) # Remove original file
        move(abs_path, file_path) # Move new file

    def write_settings_XML_file(self):
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
                if parameter_element.attrib['batch'].lower() == "true":
                    batch_id = assign_batch_id(parameter_element.attrib['varName'])
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
        for root, dirs, files in os.walk(self.screenshot_output_path):
            for output_file in files:
                for interesting_file_type in ['*.zip','*.mov','*_3600.png']:
                    if fnmatch(output_file, interesting_file_type):
                        old_path = os.path.join(root, output_file)
                        new_path = os.path.join(self.output_folder, output_file)
                        move(old_path, new_path)

    def delete_unnecessary_files(self, check=True):
        if check == True:
            confirm = raw_input('Are you sure you want to delete unnecessary files? [type yes] ')
            if confirm.lower() != 'yes':
                return

        rmtree(self.screenshot_output_path)

    def autodetect_file_paths(self):
        cwd = os.getcwd()
        proposed_model_path = parent_dir(cwd)
        #proposed_params_path = process_path(os.path.join(proposed_model_path, 'Simulation', 'params.xml'))
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
            self.user_input_io_xml()
            return False

    def open_a_params_file(self, path):
        new_params_path = ''
        if path.endswith('.txt') or path.endswith('.xml'):
            self.params_path = new_params_path
            self.write_settings_XML_file()
            self.update_file_path_in_elongation_model_python()


def parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def process_path(dir):
    if os.path.isdir(dir):
        if not dir.endswith('/'):
            dir += '/'
    return dir

