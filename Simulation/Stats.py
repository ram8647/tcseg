# Utility classes for inputting params and reporting stats

from __future__ import print_function
import time
import json
import datetime
import sys
from os import environ
from os import getcwd

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
   def __init__(self, folder='./'):
      """Constructs a Reporter instance and Initializes its output file.

      Creates a time stamp and an output file and prints a header to the output file.  
      The handle to the output file persists during the object's existence. Data written
      to the file with this object's methods are appended (logged) to the file.  By 
      default, the file is named 'run<timestamp>'.

      :folder the folder where the output file will be stored. Defaults to CWD.
      """
      self.stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
      self.fname = folder + 'run' + self.stamp
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
   
   def inputParamsFromFile(self, fname):
     '''Inputs parameters from the designated file

     :file the file name (just the file, not complete path)
           parameters are stored as rows of the form: attr value
     :folder the (optional) name of the path to the file, defaults to CWD
     :return a dictionary with (key,value) parameter bindings
     '''
     print('Reading params: reporter = ', self.reporter)
     myprint(self.reporter, '---------------------- Stats: Reading params  -----------\n')
     global dict; dict = {}
     print('params file = ' , fname)
     myprint(self.reporter, 'params file = ', fname, '\n')

     # Read the parameters file into the dictionary, dict
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
