from tempfile import mkstemp
from shutil import move
from os import remove, close
from fnmatch import fnmatch
import fnmatch
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, parse

# Todo: Change these ghastly string manipulations into os.path.join() calls
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

        try:
            self.read_xml()
        except IOError:
            if not _silent:
                print 'No file paths set yet! Please specify them...'
                self.user_input_io_xml()
                self.write_settings_XML_file()

    def user_input_io_xml(self):
        # Have the user input the file paths
        self.model_path = raw_input('Where is folder containing ElongationModel.cc3d? ')
        if not self.model_path.endswith('/'):
            self.model_path = params_path = '/'
        self.params_path = raw_input('Where is params.txt (or params.xml)? ')
        self.output_folder = raw_input('Where do you want to keep output PNG and VTK? ')
        if not self.output_folder.endswith('/'):
            self.output_folder = params_path = '/'
        self.cc3d_command_dir = raw_input('Where is compucell3d.command? ')

        self.construct_additional_paths()

    def read_xml(self):
        inpath = os.path.join(os.getcwd(), 'ModelIOManager_Settings.xml')
        if not self.silent:
            print 'Reading file paths from: {}'.format(inpath)
        xml_file = parse(inpath)
        xml_root = xml_file.getroot()
        for child in xml_root:
            if child.tag == 'output_folder':
                self.output_folder = child.text
            if child.tag == 'params_path':
                self.params_path = child.text
            elif child.tag == 'cc3d_command_dir':
                self.cc3d_command_dir = child.text
            elif child.tag == 'model_path':
                self.model_path = child.text

        self.construct_additional_paths()

    def construct_additional_paths(self):
        self.simulation_folder_path = os.path.join(self.model_path, 'Simulation')
        self.parameter_scan_specs_xml_file_path = os.path.join(self.model_path, 'Simulation/ParameterScanSpecs.xml')
        self.elongation_model_python_path = os.path.join(self.model_path, 'Simulation/ElongationModel.py')

        for dir in os.listdir(self.output_folder):
            if fnmatch.fnmatch(dir, '*_ParameterScan'):
                self.screenshot_output_path = os.path.join(self.output_folder, dir)
                #if not self.screenshot_output_path.endswith('/'):
                #    self.screenshot_output_path = self.screenshot_output_path + '/' # I probably dont need this

    def update_file_path_in_elongation_model_python(self):
        file_path = self.elongation_model_python_path

        # Create a temp file
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
        outpath = os.path.join(os.getcwd(), '/ModelIOManager_Settings.xml')
        print 'Saving settings to: {}'.format(outpath)
        ElementTree(root).write(outpath)