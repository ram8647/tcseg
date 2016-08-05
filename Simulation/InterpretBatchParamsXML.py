from xml.etree.ElementTree import ElementTree, parse
from itertools import product
from collections import OrderedDict

# TODO: Add a feature to map certain variables onto other; so that r_mitosis 1 2 and 3 are synced, for example
# TODO: add custom processing of certain variables, like r_grow

def params_dict_for_batch(batch_iteration, xml_path, param_scan_specs_path):
    '''
    Generate a parameter dictionary corresponding to our current batch run

    :param batch_iteration: the batch run number: like run0, run1, etc.
    :param xml_path: the file path to the XML that will be decomposed into our dictionary
    :param param_scan_specs_path: the filepath to the ParameterScanSpecs.xml, which we will manipulate
     to make CompuCell run batches properly
    :return: a dictionary corresponding to our current batch run
    '''

    super_dict = OrderedDict()
    batch_vars_dict = OrderedDict()
    batch_id_to_param_name_table = OrderedDict()

    xml_file = parse(xml_path)
    xml_root = xml_file.getroot()

    # Generate a unique ID for each parameter that changes between runs, and link its name to its id in a table
    def assign_batch_id(_name):
        new_batch_id = 'batch_id_{}'.format(len(batch_vars_dict))
        batch_id_to_param_name_table[new_batch_id] = _name
        return new_batch_id

    # Parse the params_package file, adding normal parameters to 'super_dict' and batch parameters
    # to a special 'batch_dict.' Each entry of the batch dictionary contains a list, wherein each element
    # is a value that will be sweeped.
    for parameter_element in xml_root.iter('param'):
        if parameter_element.attrib['batch'].lower() == "false":
            super_dict[parameter_element.attrib['varName']] = parameter_element.text

        elif parameter_element.attrib['batch'].lower() == "true":
            batch_id = assign_batch_id(parameter_element.attrib['varName'])
            batch_vars_dict[batch_id] = []
            for values_element in parameter_element.iter('BatchValue'):
                batch_vars_dict[batch_id].append(values_element.text)

    # Generate a tuple for all possible combinations of batch values
    all_combinations_of_params = list(product(*[batch_vars_dict[key] for key in batch_vars_dict]))

    # Update parameter scan specs, just in case
    num_runs = len(all_combinations_of_params)
    update_parameter_scan_specs(num_runs=num_runs, scan_spec_path=param_scan_specs_path)

    # Add the proper combination of batch variables to the super_dict and return it.
    combination_of_interest = all_combinations_of_params[batch_iteration]
    for i, key in enumerate(batch_vars_dict):
        super_dict[batch_id_to_param_name_table[key]] = combination_of_interest[i]
    return super_dict