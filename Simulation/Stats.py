# Utility classes for inputting params and reporting stats

import time
import datetime
import sys
from os import environ
from os import getcwd

#  NOTE: These paths assume that tcseg is a sibling directory to CC3D_3.7.1
global PARAMS_FOLDER; PARAMS_FOLDER  =  '../tcseg/Simulation/'    # Root directory of params file
global RUNS_FOLDER;  RUNS_FOLDER  =  '../tcseg/Simulation/runs/'    


class StatsReporter: 
   '''Utility class for reporting stats'''
   def __init__(self):
      '''Initializes the output file for reporting stats'''
      self.stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
      self.fname = RUNS_FOLDER + 'run' + self.stamp
##      self.fname = os.getcwd() + '/runs/'  + 'run' + self.stamp
      print 'Creating StatsReporter opening file ', self.fname
      self.outfile = open(self.fname, 'w')
      self.outfile.write('---- Starting Run @ yymmdd-hhmmss ' + self.stamp + '--------\n')
      self.outfile.close()

   def beginOutputStats(self):
     '''Redirects output to the current run file'''
     print "<<<<<<< Redirecting output to ", self.fname
     sys.stdout = open(self.fname, 'a')
     
   def endOutputStats(self):
     '''Redirects output to stdout'''
     print "<<<<<<< Redirecting output to stdout"
     self.outfile.close()
#     sys.stdout.close()
     sys.stdout = sys.__stdout__

   def displayStats(self, list=[]):
     '''Displays stats in the terminal
 
      :param list takes the form ['attr1', val1, 'attr2', val2, ..., ]

     '''     
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     print '---------------------- Stats --------------------'
     print stamp
     it = iter(list)
     for i in it:
       attr = i
       value = next(it)
       print attr,'=',value
     print '--------------------------------------------------'



class ParamsContainer:
   '''Manages inputting parameter settings from a file'''

   global dict

   def __init__(self):
     self.params = {}   # dictionary that stores the params
     self.reporter = StatsReporter()     
   
   @classmethod
   def is_number(self,str):
     '''Returns true if str is a number'''
     try:
       float(str)
       return True
     except ValueError:
       return False

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

   def getNumberParam(self, key, params = None):
     '''Returns the value for a number key or 0 if missing

     :params a dictionary of parameter (key,value) bindings
     :key a particular key in the dictionary, possibly absent
     '''

     if params == None:
       params = dict
     result = params[key] if key in params else 0     
     print '>>>> Parameter setting',key,'=',result
     return result

   def getBooleanParam(self, key, params = None):
     '''Returns the value for a boolean key or 0 if missing

     :params a dictionary of parameter (key,value) bindings
     :key a particular key in the dictionary, possibly absent
     '''
     if params == None:
       params = dict
     result = params[key] if key in params else False     
     print '>>>> Parameter setting',key,'=',result
     return result

   def inputParamsFromFile(self, file):
     '''Inputs parameters from the designated file

     :file the file name (just the file, not complete path)
           parameters are stored as rows of the form: attr value
     :return a dictionary with (key,value) parameter bindings
     '''
     self.reporter.beginOutputStats()
     print '---------------------- Stats: Reading params  -----------'
     global dict;
     dict = {}
     fname = PARAMS_FOLDER + file + ".txt"
##     fname = os.getcwd() + '/'  + file + ".txt"
     print 'params file = ', fname
     with open(fname) as f:
       for line in f:    
         line = line.strip('\n')
         if line and not line[0] == '#':
#           print line.strip('\n')
           (key,val) = line.split()
           if ParamsContainer.is_number(val):
#             print(val, 'is a number')
             dict[key] = float(val)
           elif val in ("False", "True"):
             dict[key] = ParamsContainer.str2bool(val)
           else:
             dict[key] = val

     print '\tReading data from file ', fname
     for k,v in dict.items():
       print '\t',k,'-->',v
     print '---------------------- Stats: Done  ---------------------'
     self.reporter.endOutputStats()
     return dict


def main():
   ''' Code to test methods in this class.'''
     
   reporter = StatsReporter()
   reporter.beginOutputStats()
   print 'Reporting output stats'

   params = ParamsContainer()
   params_dict = params.inputParamsFromFile('params')
   r_mitosis_R0 = params.getNumberParam('r_mitosis_R0')
   r_mitosis_R1 = params.getNumberParam('r_mitosis_R1') 
   r_mitosis_R2 = params.getNumberParam('r_mitosis_R2')
   r_mitosis_R3 = params.getNumberParam('r_mitosis_R3')
   bogus = params.getBooleanParam('bogus')
   speed_up_sim = params.getBooleanParam('speed_up_sim', params_dict)

   print speed_up_sim
   if bool(speed_up_sim) and speed_up_sim: 
     print 'Speeding up'
   else:
     print 'Not speeding up'

   print r_mitosis_R0, r_mitosis_R1, r_mitosis_R2, r_mitosis_R3
   print r_mitosis_R0 + r_mitosis_R3
   reporter.endOutputStats()
   print 'End of the test run'


def test(): 
  params = ParamsContainer()
  params.inputParamsFromFile('params')
#  params.str2bool("ralp")
  print params.contains("key")

# To test the methods in this file, uncomment the next statement
#main()  #  Run the tests
#test()
