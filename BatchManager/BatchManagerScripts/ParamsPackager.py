import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, parse
import xml.dom.minidom as minidom
from ModelIOManager import IOManager
import os
import json


class valueTypeChecker:
    @classmethod
    def is_number(self,str):
        """Returns true if str is a number"""
        try:
            float(str)
            return True
        except ValueError:
            return False

    @classmethod
    def is_list(self,str):
        '''Returns true if str is a list'''
        str = str.strip()
        return str.startswith('[') and str.endswith(']')

    @classmethod
    def str2list(self,str):
        '''Converts string of form [1,2,3] into a list'''
        return json.loads(str)

    @classmethod
    def str2bool(self,str):
        '''Converts str to its boolean equivalent'''
        if str in ("False", "false"):
            return False
        if str in ("True", "true"):
            return True
        raise ValueError(str + " cannot be converted to boolean")


def load_params_dict(fname):
    '''
    :param fname: the file path for params.txt
    :return: the params dictionary
    '''
    dict = {}
    with open(fname) as f:
        for line in f:
            if 1==1:
                line = line.strip('\n')
                if line and not line[0] == '#':
                    (key, val) = line.split()
                    if valueTypeChecker.is_number(val):
                        dict[key] = float(val)
                    elif val in ("False", "True"):
                        dict[key] = valueTypeChecker.str2bool(val)
                    elif valueTypeChecker.is_list(val):
                        dict[key] = valueTypeChecker.str2list(val)
                    else:
                        dict[key] = val
            #except:
            #    print('Error reading line: {}'.format(line))
    return dict

def create_xml_from_params_dict(param_dict):
    '''
    :param param_dict: the parameter dictionary
    :return: a pretty string representation of the parameter dictionary as XML
    '''
    root = ET.Element('params_pkg')
    root.set('manager_version','beta_1')
    root.set('name','Test')
    for param_name, param_value in sorted(param_dict.iteritems()):
        param_element = ET.SubElement(root, 'param')
        param_element.set('varName', param_name)
        param_element.set('batch', 'False')
        param_element.text = str(param_value)
    rough_string = ET.tostring(root)
    reparsed = minidom.parseString(rough_string)
    pretty_str = reparsed.toprettyxml(indent="\t")
    return pretty_str

def write_xml_to_sim_directory(xml_as_str, io_manager):
    '''
    Write the params.xml to the Simulation directory
    :param xml_as_str: the string representation of an XML file
    '''

    outpath = os.path.join(io_manager.simulation_folder_path, 'params.xml')
    print 'Saving file to: {}'.format(outpath)
    with open(outpath, 'w') as f:
        f.write(xml_as_str)