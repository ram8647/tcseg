import os
import shutil
from xml.etree.ElementTree import ElementTree, parse
from ModelIOManager import IOManager
from fnmatch import fnmatch

def reset():
    io_manager = IOManager()
    parameter_scan_specs_xml_file_path = io_manager.parameter_scan_specs_xml_file_path
    path_to_clear = io_manager.output_folder

    print 'Modifying {}'.format(parameter_scan_specs_xml_file_path)
    print 'Deleting contents of {}'.format(path_to_clear)

    #reset the compucell settings to begin at the beginning of the batch run
    xml_file = parse(parameter_scan_specs_xml_file_path)
    xml_root = xml_file.getroot()
    for parameter_element in xml_root.iter('Parameter'):
        parameter_element.set('CurrentIteration', '0')
    ElementTree(xml_root).write(parameter_scan_specs_xml_file_path)

    #remove the outputted vtks and pngs
    for root, dirs, files in os.walk(path_to_clear):
        for d in dirs:
            if not fnmatch(d, '*_ParameterScan') or not fnmatch(d, 'css') or not fnmatch(d, 'js'):
            	shutil.rmtree(os.path.join(root, d))
        for f in files:
            if not fnmatch(f, '*.js') or not fnmatch(f, '*.css'):
                os.remove(os.path.join(root, f))