# This file contains functions for outputting and displaying stats
# for the RewrittenSarrazin model.

# From Terri 
# Inputs to track
#   The regions undergoing mitosis (R0-R3) and the fraction
#   The growth allowed in each region (r_grow_R0)
#   Fraction AP oriented
#   k1-k3 of the force step for both ML and AP forces 

# Outputs 
#  AP length of embryo 
#  Area of embryo
#  AP length of growth zone
#  Area of the growth zone
#  Total cell number

import time
import datetime

class Stats:
   # Displays stats in the run-time listing
   @classmethod
   def displayStats(self, label, value):
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     print label,'=',value
     
#     print '---------------------- Stats --------------------'
#     print stamp


   # Displays a list of stats, one per line. The list should look like this:
   # [ 'attribute', value, 'attr2', value2, ..., ]
   @classmethod
   def displayStats(self, list):
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     print '---------------------- Stats --------------------'
     print stamp
     it = iter(list)
     for i in it:
       attr = i
       value = next(it)
       print attr,'=',value
     print '--------------------------------------------------'
     


   # Outputs data to a file whose path is fixed relative to the CC3D folder
   @classmethod
   def outputStats(self):
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     fname = '../tcseg/runs/run' + stamp
     outfile = open(fname, 'w')
     outfile.write('---------------------- Stats --------------------\n')
     outfile.write(stamp + '\n')
     outfile.close()

