from xml.etree.ElementTree import ElementTree, parse
from itertools import product
from collections import OrderedDict
import ast


def params_dict_for_batch(batch_iteration, xml_path, param_scan_specs_path):
    '''
    Generate a parameter dictionary corresponding to our current batch run

    :param batch_iteration: the batch run number: like run0, run1, etc.
    :param xml_path: the file path to the XML that will be decomposed into our dictionary
    :param param_scan_specs_path: the filepath to the ParameterScanSpecs.xml, which we will manipulate
     to make CompuCell run batches properly
    :return: a dictionary corresponding to our current batch run
    '''

    raw_dict = OrderedDict()
    batch_vars_dict = OrderedDict()
    batch_id_to_param_name_table = OrderedDict()

    xml_file = parse(xml_path)
    xml_root = xml_file.getroot()

    # Generate a unique ID for each parameter that changes between runs, and link its name to its id in a table
    def assign_batch_id(_name):
        new_batch_id = 'batch_id_{}'.format(len(batch_vars_dict))
        batch_id_to_param_name_table[new_batch_id] = _name
        return new_batch_id

    # Parse the params_package file, adding normal parameters to 'raw_dict' and batch parameters
    # to a special 'batch_dict.' Each entry of the batch dictionary contains a list, wherein each element
    # is a value that will be sweeped.
    for parameter_element in xml_root.iter('param'):
        if parameter_element.attrib['batch'].lower() == "false":
            raw_dict[parameter_element.attrib['varName']] = ast.literal_eval(parameter_element.text)

        elif parameter_element.attrib['batch'].lower() == "true":
            batch_id = assign_batch_id(parameter_element.attrib['varName'])
            batch_vars_dict[batch_id] = []
            for values_element in parameter_element.iter('BatchValue'):
                batch_vars_dict[batch_id].append(ast.literal_eval(values_element.text))

    # If there are no variables to sweep, simply apply the variable rules and return it...
    if len(batch_vars_dict) == 0:
        update_parameter_scan_specs(num_runs=1, scan_spec_path=param_scan_specs_path)
        final_dict = process_dictionary(raw_dict)
        return final_dict

    # ...otherwise, we'll add the batch values in apropriately, first by generating a tuple
    # for all possible combinations of batch values
    all_combinations_of_params = list(product(*[batch_vars_dict[key] for key in batch_vars_dict]))

    # Update parameter scan specs so CompuCell will run the appropriate number of times, just in case
    num_runs = len(all_combinations_of_params)
    update_parameter_scan_specs(num_runs=num_runs, scan_spec_path=param_scan_specs_path)

    # Add the proper combination of batch variables to the raw_dict and return it.
    combination_of_interest = all_combinations_of_params[batch_iteration]
    for i, key in enumerate(batch_vars_dict):
        raw_dict[batch_id_to_param_name_table[key]] = combination_of_interest[i]

    final_dict = process_dictionary(raw_dict)
    return final_dict


def update_parameter_scan_specs(num_runs, scan_spec_path):
    '''
    Manipulate the ParameterScanSpecs.xml to make CompuCell run our simulation the correct number of times

    :param num_runs: the total number of times that the simulation should run
    :param scan_spec_path: the filepath to the ParameterScanSpecs.xml,
    '''
    scan_spec_values = []
    for iteration_num in range(num_runs):
        scan_spec_values.append('\"{{\\\'batch_on\\\': True, \\\'iteration\\\': {}}}\"'.format(iteration_num))
    scan_spec_values_str_rep = ','.join(scan_spec_values)

    xml_file = parse(scan_spec_path)
    xml_root = xml_file.getroot()
    for values_element in xml_root.iter('Values'):
        values_element.text = scan_spec_values_str_rep
    ElementTree(xml_root).write(scan_spec_path)


def process_dictionary(dict):
    '''
    :param dict: the raw dictionary
    :return: a dictionary where all the values have been checked and manipulated if needed
    '''
    if 'r_mitosis_R123' in dict.keys():
        val = dict['r_mitosis_R123']
        dict['r_mitosis_R1'] = val
        dict['r_mitosis_R2'] = val
        dict['r_mitosis_R3'] = val
        del dict['r_mitosis_R123']

    if 'r_grow_R123' in dict.keys():
        val = dict['r_grow_R123']
        dict['r_grow_R1'] = val
        dict['r_grow_R2'] = val
        dict['r_grow_R3'] = val
        del dict['r_grow_R123']

    if 'r_mitosis_GZ' in dict.keys():
        val = dict['r_mitosis_GZ']
        dict['r_mitosis_R2'] = val
        dict['r_mitosis_R3'] = val
        del dict['r_mitosis_GZ']

    if 'r_grow_GZ' in dict.keys():
        val = dict['r_grow_GZ']
        dict['r_grow_R2'] = val
        dict['r_grow_R3'] = val
        del dict['r_grow_GZ']

    for i in range(3):
        default_growth_rate = 0.02
        if dict['r_mitosis_R{}'.format(i)] == [0.0] * 3
            dict['r_grow_R{}'.format(i)] = [0.0] * 3
        else:
            if not 'r_grow_R{}'.format(i) in dict:
                dict['r_grow_R{}'.format(i)] = [default_growth_rate] * 3


    return dict