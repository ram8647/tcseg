# Test the param methods and functions

import time
import datetime

class StatsReporter: 
   '''Utility class for reporting stats'''
#   def __init__(self):

   def outputStats(self):
     '''Outputs stats to a file'''
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     fname = Params.RUNS_FOLDER + 'run' + stamp
     outfile = open(fname, 'w')
     outfile.write('---------------------- Stats --------------------\n')
     outfile.write(stamp + '\n')
     outfile.close()

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

   PARAMS_FOLDER = './'  # Root directory of params file
   RUNS_FOLDER = './'    

   def __init__(self):
     self.params = {}   # dictionary that stores the params
   
   @classmethod
   def is_number(self,str):
     '''Returns treu if str is a number'''
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

   @classmethod
   def getNumberParam(self,params,key):
     '''Returns the value for a number key or 0 if missing

     :params a dictionary of parameter (key,value) bindings
     :key a particular key in the dictionary, possibly absent
     '''
     result = params[key] if key else 0     
     print '>>>> Parameter setting',key,'=',result
     return result

   @classmethod
   def getBooleanParam(self,params,key):
     '''Returns the value for a boolean key or 0 if missing

     :params a dictionary of parameter (key,value) bindings
     :key a particular key in the dictionary, possibly absent
     '''
     result = params[key] if key else False     
     print '>>>> Parameter setting',key,'=',result
     return result

   # Inputs parameter settings from file and returns them as a dictionary
   # Parameters are stored as rows in a text file. Each row takes the form
   #        attribute value
   # This method returns a dictionary with those associations
   @classmethod
   def inputParamsFromFile(self, file):
     '''Inputs parameters from the designated file

     :file the file name (just the file, not complete path)
           parameters are stored as rows of the form: attr value
     :return a dictionary with (key,value) parameter bindings
     '''
     print '---------------------- Stats: Reading params  -----------'
     self.dict = {}
     fname = ParamsContainer.PARAMS_FOLDER + file + ".txt"
     with open(fname) as f:
       for line in f:    
         line = line.strip('\n')
         if line and not line[0] == '#':
#           print line.strip('\n')
           (key,val) = line.split()
           if ParamsContainer.is_number(val):
#             print(val, 'is a number')
             self.dict[key] = float(val)
           elif val in ("False", "True"):
             self.dict[key] = ParamsContainer.str2bool(val)
           else:
             self.dict[key] = val

     print '\tReading data from file ', fname
#     print '\tParams ', dict
     for k,v in self.dict.items():
       print '\t',k,'-->',v
     print '---------------------- Stats: Done  ---------------------'
     return self.dict

def main():
   params = ParamsContainer()
   params_dict = params.inputParamsFromFile('params')
   r_mitosis_R0 = params.getNumberParam(params_dict, 'r_mitosis_R0')
   r_mitosis_R1 = params.getNumberParam(params_dict, 'r_mitosis_R1') 
   r_mitosis_R2 = params.getNumberParam(params_dict, 'r_mitosis_R2')
   r_mitosis_R3 = params.getNumberParam(params_dict, 'r_mitosis_R3')
   speed_up_sim = params.getBooleanParam(params_dict,'speed_up_sim')

   print speed_up_sim
   if bool(speed_up_sim) and speed_up_sim: 
     print 'Speeding up'
   else:
     print 'Not speeding up'

   print r_mitosis_R0, r_mitosis_R1, r_mitosis_R2, r_mitosis_R3
   print r_mitosis_R0 + r_mitosis_R3

   print 'Reporting output stats'
   reporter = StatsReporter()
   reporter.displayStats()


# To test the methods in this file, uncomment the next statement
#main()  #  Run the tests
