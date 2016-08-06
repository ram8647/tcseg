from xml.etree.ElementTree import ElementTree, parse
from itertools import product
from collections import OrderedDict
import ast
from ModelIOManager import IOManager
import fnmatch

import csv

def create_summary():
    '''
    write a file that summarizes all the batch runs
    '''
    manager = IOManager()
    params_path = manager.params_path
    outpath = '/Users/jeremyfisher/Desktop/summary.csv'

    if params_path.endswith('.txt'):
        with open(params_path, 'r') as in_file:
            with open(outpath, 'w') as out_file:
                in_file.write(out_file.read())

    elif params_path.endswith('.xml'):
        # Todo: summary should not include r_mitosis123
        #ignore_parameters = ['r_mitosis_R123']

        batch_vars_dict = OrderedDict()

        xml_file = parse(params_path)
        xml_root = xml_file.getroot()

        for parameter_element in xml_root.iter('param'):
            if parameter_element.attrib['batch'].lower() == "true":
                variable_name = parameter_element.attrib['varName']
                print 'Including {}...'.format(variable_name)
                batch_vars_dict[variable_name] = []
                for values_element in parameter_element.iter('BatchValue'):
                    print '\tand {}...'.format(values_element.text)
                    new_batch_value = ast.literal_eval(values_element.text)
                    if fnmatch.fnmatch(variable_name, 'r_mitosis_R*') or fnmatch.fnmatch(variable_name, 'r_grow_R*'):
                        first_var = new_batch_value[0]
                        if new_batch_value == [first_var] * 3:
                            new_batch_value = new_batch_value[0]
                    batch_vars_dict[variable_name].append(new_batch_value)

        with open(outpath, 'wb') as csvfile:
            summary_writer = csv.writer(csvfile, delimiter=';')
            summary_writer.writerow(['run #']+batch_vars_dict.keys())

            all_combinations_of_params = product(*[batch_vars_dict[key] for key in batch_vars_dict])
            for run_number, combo in enumerate(all_combinations_of_params):
                combo_list = [str(element) for element in combo]
                summary_writer.writerow([run_number]+combo_list)

    else:
        print 'Unknown params file-type!'

