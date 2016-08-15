# Utility classes for inputting params and reporting stats

from __future__ import print_function
import time
import json
import datetime
from xml.etree.ElementTree import ElementTree, parse
from itertools import product
from collections import OrderedDict
import ast
import PostProcessParamsXML

#  NOTE: These paths assume that tcseg is a sibling directory to CC3D_3.7.1
global PARAMS_FOLDER; PARAMS_FOLDER  = './' #  '../tcseg/Simulation/'    # Root directory of params file
global RUNS_FOLDER;  RUNS_FOLDER  =  './' #'../tcseg/Simulation/runs/'    

def myprint(reporter=None, *args):
    """My custom print() function."""
    # Adding new arguments to the print function signature
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    # print('myprint reporter = ', reporter)
    if reporter:
        return reporter.rprint(*args)
    else:
        return __builtins__.print(*args)

class StatsReporter:
    """Utility class for reporting stats

    Each instance (object) of this class opens an output file. To
    create multiple reports during a run, create multiple instances.
    The methods, print(), printLn(), and
    printAttrValue() print their arguments to the output file.

    """
    def __init__(self, batch = False, batch_iteration = 0, folder='./'):
        """Constructs a Reporter instance and Initializes its output file.

        Creates a time stamp and an output file and prints a header to the output file.
        The handle to the output file persists during the object's existence. Data written
        to the file with this object's methods are appended (logged) to the file.  By
        default, the file is named 'run<timestamp>'.

        :folder the folder where the output file will be stored. Defaults to CWD.
        """
        self.batch = batch
        self.stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
        if batch:
            self.fname = '{}batch_run_{}.txt'.format(folder,batch_iteration)
        elif not batch:
            self.fname = folder + 'run' + self.stamp + '.txt'
        print('Creating StatsReporter opening file ', self.fname)
        self.outfile = open(self.fname, 'w', 1)
        self.outfile.write('---- Starting Run @ yymmdd-hhmmss ' + self.stamp + '--------\n')
        self.outfile.close()

    def rprint(self, *args):
        """Prints a variable list of arguments, space separated, to this object's outfile.

        :args is a Python list.
        :newline Set to True to print newline at end

        E.g., Where obj is a reference to a StatsPrinter object,  obj.print(1, 2, 3)
        will print its args on a single line followed  by a new line.

            1 2 3
        """
        try:
            self.outfile = open(self.fname, 'a', 1)
            for arg in args:
                self.outfile.write( str(arg) + " ")
            self.outfile.close()
        except IOError:
            print("I/O error")

    def printAttrValue(self, newline=False, **args):
        """Prints a variable list of attr=value pairs, one per line, to this object's outfile.

        :args is a Python dictionary.
        :newline set to true if printing attr=value per line

        E.g., Where obj is a reference to a StatsPrinter object, and a1=1 and a2=2,
                 obj.print(a1=a1, a2=a2)
        will print its args on a single line followed  by a new line.

            a1=1
            a2=1

        """
        nl = '\n' if newline else ' '
        self.outfile = open(self.fname, 'a', 1)
        for k,v in args.iteritems():
            self.outfile.write( str(k) + "=" + str(v) + nl)
        self.outfile.write( '\n')
        self.outfile.close()


    def printLn(self, *args):
        """Prints a variable list of arguments, one per line, to this object's outfile.

        :args is a Python list.

        E.g., Where obj is a reference to a StatsPrinter object,  obj.printLn(1, 2)
        will print its args on a single line followed  by a new line.

            1
            2
        """
        self.outfile = open(self.fname, 'a', 1)
        for arg in args:
            self.outfile.write( str(arg) + "\n")
        self.outfile.close()


class ParamsContainer:
    '''Manages input parameter settings from a file'''

    global dict         # Dictionary that stores the parameters

    def __init__(self, reporter=None):
        self.params = {}   # dictionary that stores the params
        self.reporter = reporter

    def inputParamsFromFile(self, fname, batch_iteration, param_scan_spec='./'):
        '''
        Output a dictionary from a .txt or .xml file. If it is a .xml file, it also requires the
        run number (e.g. run0, run1, etc...) and the file path to the ParameterScanSpecs.xml file

        :param fname: path to the .txt or .xml file
        :param batch_iteration: the run number (e.g. run0, run1, etc...)
        :param param_scan_spec: path to the ParameterScanSpecs.xml file
        :return: a dictionary with proper (key,value) parameter bindings
        '''

        print('Reading params: reporter = ', self.reporter)
        myprint(self.reporter, '---------------------- Stats: Reading params  -----------\n')
        global dict; dict = {}
        print('params file = ' , fname)
        myprint(self.reporter, 'params file = ', fname, '\n')

        # Read the parameters file into the dictionary, dict
        if fname.endswith('.txt'):
            with open(fname) as f:
                for line in f:
                    try:
                        line = line.strip('\n')
                        if line and not line[0] == '#':
                            key = line.split()[0]
                            val = ' '.join(line.split()[1:])
                            if ParamsContainer.is_number(val):
                                dict[key] = float(val)
                            elif val in ("False", "True"):
                                dict[key] = ParamsContainer.str2bool(val)
                            elif ParamsContainer.is_list(val):
                                dict[key] = ParamsContainer.str2list(val)
                            else:
                                dict[key] = val
                    except:
                        raise NameError('Could not parse line: \'{}\''.format(line))
        elif fname.endswith('.xml'):
            dict = params_dict_for_batch(batch_iteration = batch_iteration,
                                         params_xml_path=fname,
                                         param_scan_specs_path=param_scan_spec)

        myprint(self.reporter, '\tReading data from file ', fname, '\n')

        for k,v in sorted(dict.items()):
            myprint(self.reporter,'\t',k,'-->',v, '\n')
        myprint(self.reporter, '---------------------- Stats: Done Reading params ---------------------\n')
        return dict

    def getNumberParam(self, key, params = None):
        """
        Returns the value for a number key or 0 if missing

        :params a dictionary of parameter (key,value) bindings
        :key a particular key in the dictionary, possibly absent
        """

        if params == None:
            params = dict
        result = params[key] if key in params else 0
        myprint(self.reporter, '>>>> Parameter setting',key,'=',result, '\n')
        return result

    def getListParam(self, key, params = None):
        """
        Returns the value for a number key or 0 if missing

        :params a dictionary of parameter (key,value) bindings
        :key a particular key in the dictionary, possibly absent
        """

        if params == None:
            params = dict
        result = params[key] if key in params else []
        myprint(self.reporter, '>>>> Parameter setting',key,'=',result, '\n')
        return result

    def getBooleanParam(self, key, params = None):
        """
        Returns the value for a boolean key or 0 if missing

        :params a dictionary of parameter (key,value) bindings
        :key a particular key in the dictionary, possibly absent
        """
        if params == None:
            params = dict
        result = params[key] if key in params else False
        myprint(self.reporter, '>>>> Parameter setting',key,'=',result,'\n')
        return result

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

    def contains(self, key, params=None):
        if params==None:
            params = dict
        return True if key in params else False


def params_dict_for_batch(batch_iteration, params_xml_path, param_scan_specs_path):
    '''
    Generate a parameter dictionary corresponding to our current batch run

    :param batch_iteration: the batch run number, like run0, run1, etc.
    :param params_xml_path: the file path to the XML that will fed into our dictionary
    :param param_scan_specs_path: the filepath to the ParameterScanSpecs.xml, which we will manipulate
     to make CompuCell run batches properly
    :return: a dictionary corresponding to our current batch run
    '''
    def has_children(xml_element):
        return True if len(list(xml_element)) else False

    raw_dict = OrderedDict()
    batch_vars_dict = OrderedDict()
    batch_id_to_param_name_table = OrderedDict()

    xml_file = parse(params_xml_path)
    xml_root = xml_file.getroot()

    # Generate a unique ID for each parameter that changes between runs, and link its name to its id in a table
    def assign_batch_id(_name):
        new_batch_id = 'batch_id_{}'.format(len(batch_vars_dict))
        batch_id_to_param_name_table[new_batch_id] = _name
        return new_batch_id

    # Parse the params_package file, adding normal parameters to 'raw_dict' and batch parameters
    # to a special 'batch_dict.' Each entry of the batch dictionary contains a list, wherein each element
    # is a value that will be swept.
    for parameter_element in xml_root.iter('param'):
        # First, we'll assume that any param element with children is a variable that should be swept
        if has_children(parameter_element):
            var_name = parameter_element.attrib['varName']
            batch_id = assign_batch_id(var_name)
            batch_vars_dict[batch_id] = []
            for values_element in parameter_element.iter('BatchValue'):
                batch_vars_dict[batch_id].append(ast.literal_eval(values_element.text))

        # If it doesnt have children, just pull the interior text into our dictionary
        elif not has_children(parameter_element):
            raw_dict[parameter_element.attrib['varName']] = ast.literal_eval(parameter_element.text)

    # If there are no variables to sweep, simply apply the dictionary rules and return it...
    if len(batch_vars_dict) == 0:
        update_parameter_scan_specs(num_runs=1, scan_spec_path=param_scan_specs_path)
        final_dict = PostProcessParamsXML.process_dictionary(raw_dict)
        return final_dict

    # ...otherwise, we'll add the batch values in appropriately, first by generating a tuple
    # for all possible combinations of batch values
    all_combinations_of_params = list(product(*[batch_vars_dict[key] for key in batch_vars_dict]))

    # Update parameter scan specs so CompuCell will run the appropriate number of times, just in case
    num_runs = len(all_combinations_of_params)
    update_parameter_scan_specs(num_runs=num_runs, scan_spec_path=param_scan_specs_path)

    # Add the proper combination of batch variables to the raw_dict and return it. If the name is two
    # variables combined by an &, like r_mitosis_r1&r_mitosis_r2, these will be swept together
    combination_of_interest = all_combinations_of_params[batch_iteration]
    for i, key in enumerate(batch_vars_dict):
        combined_param_names = batch_id_to_param_name_table[key]
        param_name_list = combined_param_names.split('&')
        for param_name in param_name_list:
            raw_dict[param_name] = combination_of_interest[i]

    final_dict = PostProcessParamsXML.process_dictionary(raw_dict)
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


def main():
    ''' Code to test methods in this class.'''

    reporter = StatsReporter()
    reporter.rprint('Reporting output stats')

    params = ParamsContainer(reporter)
    params_dict = params.inputParamsFromFile('params')
    r0 = params.getNumberParam('r_mitosis_R0')
    r1 = params.getNumberParam('r_mitosis_R1')
    r2 = params.getNumberParam('r_mitosis_R2')
    r3 = params.getNumberParam('r_mitosis_R3')
    bogus = params.getBooleanParam('bogus')
    speed_up_sim = params.getBooleanParam('speed_up_sim', params_dict)

    reporter.rprint("Rs: ", r0, r1, r2, r3)
    reporter.printLn(r0, r1, r2, r3)
    reporter.printAttrValue(r0=r0, r1=r1, r2=r2, r3=r3)
    reporter.rprint( r0 + r3)

    reporter.rprint(speed_up_sim)
    if bool(speed_up_sim) and speed_up_sim:
        reporter.rprint('Speeding up')
    else:
        reporter.rprint('Not speeding up')

    myprint(None, 'End of the test run')

def test():
    reporter = StatsReporter()
    myprint(reporter, 'hello', 'world')
    myprint(None, 'goodbye', 'world')

#  params = ParamsContainer()
#  params.inputParamsFromFile('params')
#  params.str2bool("ralp")
#  print(params.contains("key"))

# To test the methods in this file, uncomment the next statement
#main()  #  Run the tests
#test()
