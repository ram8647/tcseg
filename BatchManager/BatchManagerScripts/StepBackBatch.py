from ModelIOManager import IOManager
from xml.etree.ElementTree import ElementTree, parse
from fnmatch import fnmatch
import os
import shutil

def step_back(io_manager):
    current_iteration = None
    target_iteration = None

    # Figure out the current iteration and modify the scan specs file appropriately
    parameter_scan_specs_xml_file_path = io_manager.parameter_scan_specs_xml_file_path
    xml_file = parse(parameter_scan_specs_xml_file_path)
    xml_root = xml_file.getroot()
    for parameter_element in xml_root.iter('Parameter'):
        current_iteration = int(parameter_element.attrib['CurrentIteration'])
        target_iteration = current_iteration - 1

        print('Stepping up files to redo batch run {}'.format(target_iteration))

        parameter_element.set('CurrentIteration', str(target_iteration))
    ElementTree(xml_root).write(parameter_scan_specs_xml_file_path)
    
    # Remove screenshots
    for root, dirs, files in os.walk(io_manager.screenshot_output_path):
        for dir in dirs:
            if dir == str(target_iteration):
                shutil.rmtree(os.path.join(root, dir))
    
    # Remove most recent .csv and .txt in output folder
    for root, dirs, files in os.walk(io_manager.output_folder):
        for file in files:
            if fnmatch(file, '*output{}.txt'.format(target_iteration)) or fnmatch(file, '*output{}.csv'.format(target_iteration)):
                os.remove(os.path.join(root, file))