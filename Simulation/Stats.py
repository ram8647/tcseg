# This file contains functions for outputting and displaying stats
# for the RewrittenSarrazin model.

import time
import datetime

class Stats:
   @classmethod
   def displayStats(self, label, value):
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     print label,'=',value
     
#     print '---------------------- Stats --------------------'
#     print stamp

   # Outputs data to a file whose path is fixed relative to the CC3D folder
   #
   @classmethod
   def outputStats(self):
     stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
     fname = '../tcseg/runs/run' + stamp
     outfile = open(fname, 'w')
     outfile.write('---------------------- Stats --------------------\n')
     outfile.write(stamp + '\n')
     outfile.close()

