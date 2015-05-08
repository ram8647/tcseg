from Stats import StatsReporter
from Stats import ParamsContainer

from PlayerPython import * 
import CompuCellSetup
## General Note: Cell Address is relative to the anterior. So, a 0.0 address means that it is on the anterior tip.

from PySteppables import *
from PySteppablesExamples import MitosisSteppableBase
import CompuCell
import sys
import math
from random import random
from copy import deepcopy

class jeremyVector:
    def __init__(self,_x,_y):
        self.x = float(_x)
        self.y = float(_y)
        self.distance = float(math.sqrt(_x**2 + _y**2))

    def x(self): return self.x
    def y(self): return self.y
    def mag(self): return self.distance
    def set_x(self, _x):
        self.x = _x
        self.distance = math.sqrt(_x**2 + _y**2)
    def set_y(self, _y):
        self.y = _y
        self.distance = math.sqrt(_x**2 + _y**2)

    def scream(self): raise NameError("Vector x = {}, y = {}".format(self.x,self.y))

    def normalize(self):
        if self.distance > 0:
            self.x /= self.distance
            self.y /= self.distance
            self.distance = 1
        else:
            self.x = 0
            self.y = 0
    def normalVector(self):
        newVec = copy.deepcopy(self)
        newVec.normalize()
        return newVec

    def add(self, vec):
        self.x += vec.x
        self.y += vec.y
    def scale(self, scaleFactor):
        self.x *= scaleFactor
        self.y *= scaleFactor

    @classmethod
    def vecBetweenPoints(cls, _start_x, _start_y, _end_x, _end_y):
        x_disp = _end_x - _start_x
        y_disp = _end_y - _start_y
        return jeremyVector(x_disp, y_disp)

    @classmethod
    def addVecs(cls,_vecs):
        newVec = jeremyVector(0,0)
        for vec in _vecs: newVec.add(vec)
        return newVec

class VolumeStabilizer(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)

    def start(self):
        for cell in self.cellList:
            cell.targetVolume = cell.volume
            cell.targetSurface = cell.surface

            # This above code prevents the cells from immediately shrinking to nothing.

            cell.lambdaVolume = 50.0 # A high lambdaVolume makes the cells resist changing volume.
            cell.lambdaSurface = 2.0 # However, a low lambdaSurface still allows them to move easily.

            # In effect, these above two lines allow the cells to travel without squeezing, which would be unrealistic.
            
class AssignCellAddresses(SteppableBasePy): # this steppable assigns each cell an address along the AP axis
    def __init__(self,_simulator,_frequency):
        SteppableBasePy.__init__(self,_simulator,_frequency)

        self.height = 0
        self.anteriormost_cell_y = None
        self.posteriormost_cell_y = None
        self.posteriormost_cell = None
        
    def evaluateEmbryoDimensions(self):
        self.anteriormost_cell_y = 0
        self.posteriormost_cell_y = 999

        for cell in self.cellList:
            if cell.yCOM > self.anteriormost_cell_y:
                self.anteriormost_cell_y = cell.yCOM
            elif cell.yCOM < self.posteriormost_cell_y:
                self.posteriormost_cell_y = cell.yCOM
                self.posteriormost_cell = cell
            
        self.height = abs(self.anteriormost_cell_y - self.posteriormost_cell_y)
        print "self.anteriormost_cell_y: ", self.anteriormost_cell_y

    def percentBodyLengthFromAnteriorToCell(self, target_cell): # delete me if not needed!
        distance_from_anterior = abs(self.anteriormost_cell_y - target_cell.yCOM)
        return distance_from_anterior / self.height

    def yCoordOfPercentBodyLengthFromAnterior(self, percent_body_length): # delete me if not needed!
        if 0 > percent_body_length or 1 < percent_body_length: raise NameError("Paramater limits of yCoordOfPercentBodyLengthFromAnterior function exceeded")
        return self.posteriormost_cell_y + self.height*percent_body_length

    def assignRelativeAddress(self, cell):
        CompuCell.getPyAttrib(cell)["CELL_AP_ADDRESS"] = self.percentBodyLengthFromAnteriorToCell(cell)

    def assignAllRelativeAddresses(self):
        self.evaluateEmbryoDimensions()
        for cell in self.cellList:
            self.assignRelativeAddress(cell)

    def immobilizeAnteriorLobe(self,cell):
        address = CompuCell.getPyAttrib(cell)["CELL_AP_ADDRESS"]
        if address < 0.2:
            cell.lambdaSurface += (0.2 - address) * 100

    def start(self): self.assignAllRelativeAddresses()
    def step(self,mcs): self.assignAllRelativeAddresses()

class SarrazinForces(SteppableBasePy):

    def __init__(self, _simulator, _frequency, _params_container):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.params_container = _params_container

        self.y_target_offset = self.params_container.getNumberParam('y_target_offset')
        self.pull_force_magnitude = self.params_container.getNumberParam('pull_force_magnitude')
        self.pinch_force_relative_center = self.params_container.getNumberParam('pinch_force_relative_center')
        self.pinch_force_mag = self.params_container.getNumberParam('pinch_force_mag')
        self.pinch_force_falloff_sharpness = self.params_container.getNumberParam('pinch_force_falloff_sharpness')
        self.posteriormost_cell = None
        self.stripe_y = None

    def start(self):
        self.posteriormost_cell = self.getSteppableByClassName('AssignCellAddresses').posteriormost_cell

    @staticmethod
    def setstripe_y(self,stripe_y):
        self.stripe_y = stripe_y

    def step(self,mcs):

        target_coord_x = 160
        target_coord_y = self.posteriormost_cell.yCOM + self.y_target_offset

        for cell in self.cellList:
            cell.lambdaVecX = 0; cell.lambdaVecY = 0 #reset forces from the MCS
            cell_address = CompuCell.getPyAttrib(cell)["CELL_AP_ADDRESS"] # figure out where the cell is within the last 100 mcs

            ##******** Here, we'll apply the pull force: ********##

            newVec = jeremyVector.vecBetweenPoints(cell.xCOM, cell.yCOM, target_coord_x,target_coord_y) # find the direction vector
            newVec.normalize() # make the vector into a unit vector
            newVec.scale(self.pull_force_magnitude) # scale it to a standard length, so that the field has a uniform, substantial magnitude
            #newVec.scale(cell_address) # scale it again, so that posterior cells are most affected by this force

            # Finally, apply the pull force

            cell.lambdaVecX -= newVec.x
            if cell.yCOM > self.stripe_y:
                cell.lambdaVecY -= newVec.y * cell_address

            # this previous line of code scales the component parallel to the AP axis
            # as a function of each cell's location on that axis.

             ##******** And here, we'll apply the pinch force ********##

            direction_vec = (160 - cell.xCOM) # First, find the vector between the cell and the AP axis.
            try: direction_vec = direction_vec/abs(direction_vec) # normalize this vector...
            except: direction_vec = 0   # unless we get a divide by zero error, in which it must be a zero vector.

            #Here, we configure the variables that govern the pinch force

            rc = self.pinch_force_relative_center # where along the AP axis, as a percentage of body length from the posterior, should this force be most active
            f = self.pinch_force_mag # the value of the force at its greatest value
            s = self.pinch_force_falloff_sharpness # sharpness of the falloff from its strongest point

            # Beyond this point lies mathy stuff -- its all just manipulation of variables to get the

            min_zenith_loc = 1/s
            max_zenith_loc = s - min_zenith_loc
            zenith_range = max_zenith_loc - min_zenith_loc
            o = min_zenith_loc + (zenith_range * rc)
            mag = (((-1) * (s*cell_address - o)**2) + 1) * f
            if mag < 0: mag = 0

            # Finally, apply the pinch force

            cell.lambdaVecX -= direction_vec * mag

class SarrazinVisualizer(SteppableBasePy):
    def __init__(self, _simulator, _frequency):
        SteppableBasePy.__init__(self, _simulator, _frequency)
        self.vectorCLField = self.createVectorFieldCellLevelPy("Sarrazin_Force")

    def step(self, mcs):
        self.vectorCLField.clear()
        for cell in self.cellList:
            self.vectorCLField[cell] = [cell.lambdaVecX * -1, cell.lambdaVecY * -1, 0]

class lobePincher(SteppableBasePy):
    def __init__(self, _simulator, _frequency, _center_x, _center_y, _extent):
        SteppableBasePy.__init__(self, _simulator, _frequency)
        self.center_x = _center_x
        self.center_y = _center_y
        self.extent = _extent
        self.cells_to_pinch = []

    def start(self):
        for cell in self.cellList:
            if jeremyVector.vecBetweenPoints(cell.xCOM, cell.yCOM, self.center_x, self.center_y).mag() < self.extent:
                self.cells_to_pinch.append(cell)

    def step(self, mcs):
        for cell in self.cells_to_pinch:
            cell.lambdaVecY -= 100

class EN_stripe:
    def __init__(self,_relative_position,_speed_mcs,_start_mcs):
        self.relative_position = _relative_position
        self.speed = _speed_mcs
        self.start_mcs = _start_mcs

class Engrailed(SteppableBasePy):
    def __init__(self,_simulator,_frequency, _stripes, _hinder_anterior_cells, height):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.stripes = _stripes
        self.hinder_anterior_cells = _hinder_anterior_cells
        self.gene_product_field = None
        self.gene_product_secretor = None
        self.height = height
        self.stripe_y = None

    def start(self):
        if self.hinder_anterior_cells == True:
            self.gene_product_field = CompuCell.getConcentrationField(self.simulator,"EN_GENE_PRODUCT")
            self.gene_product_secretor = self.getFieldSecretor("EN_GENE_PRODUCT")
        for cell in self.cellList: # THIS BLOCK HAS BEEN JUSTIFIED OUTSIDE OF EARLIER "IF" STATEMENT (sdh)
            self.stripe_y = 645 #375
            if cell.yCOM < self.stripe_y+5 and cell.yCOM > self.stripe_y-5:
            # cellDict["En_ON"] = True
                cell.type = 2 # EN cell
                if self.hinder_anterior_cells == True:
                     self.gene_product_secretor.secreteInsideCell(cell, 1)

    def step(self, mcs):
        if (mcs != 0) and (mcs % 300 == 0) :
            self.stripe_y -= 50
            SarrazinForces.setstripe_y(SarrazinForces, self.stripe_y)
            for cell in self.cellList:
                #cellDict = CompuCell.getPyAttrib(cell)
                #print "self.stripe_y:    ", self.stripe_y
                # if cell.type == 1: #AnteriorLobe
                if cell:
                    if cell.yCOM < self.stripe_y + 6 and cell.yCOM > self.stripe_y - 6:
                        #cellDict["En_ON"] = True
                        cell.type = 2 # EN
                        #if self.hinder_anterior_cells == True:
                            #self.gene_product_secretor.secreteInsideCell(cell,1)

class SarrazinCloneVisualizer(SteppableBasePy):
    def __init__(self,_simulator,_frequency, _cell_locs):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.cellLocs = _cell_locs
        self.sarraCells = []
        self.sarrazin_clone_field = self.createScalarFieldCellLevelPy("LABELED_CLONES")
        self.sarrazin_path_field = self.createScalarFieldPy("PATH_FIELD")

    def start(self):
        ## Here, we set up the field to monitor the cells in real time, the "Labeled Clones Field"

        for cell in self.cellList:
            self.sarrazin_clone_field[cell]= 0.5

        for cell_loc in self.cellLocs:
            sarrazin_clone = self.cellField[int(cell_loc.x),int(cell_loc.y),0]
            self.sarrazin_clone_field[sarrazin_clone]= 1.0
            self.sarraCells.append(sarrazin_clone)

    def step(self,mcs):
        for cell in self.sarraCells:
            self.sarrazin_path_field[int(cell.xCOM), int(cell.yCOM), 0] = 1
            
class RegionalMitosis(MitosisSteppableBase):

   def __init__(self,_simulator,_frequency, _params_container ):
      self.statsReporter = StatsReporter()
      self.params_container = _params_container

      MitosisSteppableBase.__init__(self,_simulator, _frequency)
      self.y_GZ_mitosis_border_percent = 0.5 ## The position, in fraction of the GZ (from posteriormost EN stripe to posterior of GZ,
                                             ## of the border between mitosis regions in the GZ (measured from the posterior)
      r_mitosis_R0 = self.params_container.getNumberParam('r_mitosis_R0')
      r_mitosis_R1 = self.params_container.getNumberParam('r_mitosis_R1')
      r_mitosis_R2 = self.params_container.getNumberParam('r_mitosis_R2')
      r_mitosis_R3 = self.params_container.getNumberParam('r_mitosis_R3')
      self.r_mitosis_list=[r_mitosis_R0,r_mitosis_R1,r_mitosis_R2,r_mitosis_R3]
      
      self.window = 500 # length of window in MCS (see above)
      self.Vmin_divide = 60 # minimum volume, in pixels, at which cells can divide
      self.Vmax = 90 # maximum volume to which cells can grow
      self.mitosisVisualizationFlag = 1 # if nonzero, turns on mitosis visualization
      self.mitosisVisualizationWindow = 100 # number of MCS that cells stay labeled as having divided
      
      # Set r_grow for each region: pixels per MCS added to cell's volume
      r_grow_R0=0
      r_grow_R1=0
      r_grow_R2=0
      r_grow_R3=0.05
      self.r_grow_list=[r_grow_R0,r_grow_R1,r_grow_R2,r_grow_R3]      
      
      # t_grow_R0=self.calculate_t_grow(r_mitosis_R0)
      # t_grow_R1=self.calculate_t_grow(r_mitosis_R1)
      # t_grow_R2=self.calculate_t_grow(r_mitosis_R2)
      # t_grow_R3=self.calculate_t_grow(r_mitosis_R3)
      # self.t_grow_list=[t_grow_R0,t_grow_R1,t_grow_R2,t_grow_R3]
      
      self.fraction_AP_oriented=0.5
  
      self.statsReporter.displayStats(['rg_RO', r_grow_R0, 'rg_R1', r_grow_R1, 'rg_R2', r_grow_R2, 'rg_R3', r_grow_R3])

      
   def start(self):
      self.y_EN_pos=self.find_posterior_EN_stripe()
      self.y_EN_ant=self.find_anterior_EN_stripe()
      self.y_GZ_border=self.find_y_GZ_mitosis_border()
      for cell in self.cellList:
         region=self.assign_cell_region(cell)
         # self.initiate_cell_volume(cell)  ## Initiates cells with new volumes to distribute mitoses in time
         cellDict = CompuCell.getPyAttrib(cell)
         cellDict["growth_timer"]=self.attach_growth_timer(cell)  ## attached a countdown timer for cell growth
   
   def step(self,mcs):
      print 'Executing Mitosis Steppable'
      mitosis_list=self.make_mitosis_list()
      self.perform_mitosis(mitosis_list)
      self.y_EN_pos=self.find_posterior_EN_stripe()
      self.y_EN_ant=self.find_anterior_EN_stripe()
      self.y_GZ_border=self.find_y_GZ_mitosis_border()
      for cell in self.cellList:
         self.assign_cell_region(cell)
         self.grow_cell(cell)
      # mitosis_list=self.make_mitosis_list()
      # self.perform_mitosis(mitosis_list)

   def perform_mitosis(self,mitosis_list):
      for cell in mitosis_list:
         if self.mitosisVisualizationFlag:
            self.visualizeMitosis(cell)         # change cell type to "Mitosing"
      ### Choose whether cell will divide along AP or random orientation
         AP_divide=random()
         if AP_divide <= self.fraction_AP_oriented:
            self.divideCellOrientationVectorBased(cell,0,1,0)
         else:
            self.divideCellRandomOrientation(cell)
      if self.mitosisVisualizationFlag:
         self.mitosisVisualizationCountdown()   # Maintains cell type as "Mitosing" for a set window of time (self.mitosisVisualizationWindow)
         
   # UpdateAttributes is inherited from MitosisSteppableBase
   #  and it is called automatically by the divideCell() function
   # It sets the attributes of the parent and daughter cells:      
   def updateAttributes(self):
      parentCell=self.mitosisSteppable.parentCell
      childCell=self.mitosisSteppable.childCell
            
      childCell.targetVolume = childCell.volume
      childCell.lambdaVolume = parentCell.lambdaVolume
      childCell.targetSurface = childCell.surface
      childCell.lambdaSurface = parentCell.lambdaSurface
      parentCell.targetVolume = parentCell.volume
      parentCell.targetSurface = parentCell.surface
      childCell.type = parentCell.type
      
      parentDict=CompuCell.getPyAttrib(parentCell)
      childDict=CompuCell.getPyAttrib(childCell)
   ### Make a copy of the parent cell's dictionary and attach to child cell   
      for key, item in parentDict.items():
         childDict[key]=deepcopy(parentDict[key])
   
   def assign_cell_region(self,cell):
      cellDict=CompuCell.getPyAttrib(cell)
      yCM=cell.yCM/float(cell.volume)
      if yCM > self.y_EN_ant: # if cell is anterior to EN stripes
         cellDict["region"]=0
         # if (cell.type!=4 and cell.type!=2): # if cell is not En or mitosing
            # cell.type=1 # AnteriorLobe
      elif yCM > self.y_EN_pos: # if cell is in EN-striped region
         cellDict["region"]=1
         if (cell.type!=2 and cell.type!=4): # if cell is not En or mitosing
            cell.type=5 # Segmented
      elif yCM > self.y_GZ_border: # if cell is in anterior region of GZ
         cellDict["region"]=2
         if (cell.type!=2 and cell.type!=4): # if cell is not En or mitosing
            cell.type=3 #GZ
      else:                # if cell is in posterior region of GZ
         cellDict["region"]=3
         if cell.type!=4: #if cell is not mitosing
            cell.type=3 # GZ
      
   def initiate_cell_volume(self,cell): 
      phase=random() # chooses a phase between 0 and 1 to initialize cell volume
      volume_difference=self.Vmin_divide - cell.volume
      new_volume=phase*volume_difference + cell.volume
      cell.targetVolume = new_volume
      
   def attach_growth_timer(self,cell):
      phase=random() # picks a random phase between 0 and 1 to initialize cell growth timer
      growth_timer=phase
      return growth_timer
      
   def grow_cell(self,cell):
      cellDict=CompuCell.getPyAttrib(cell)
      region=cellDict["region"]
      r_grow=self.r_grow_list[region]
      if cellDict["growth_timer"] >= 1:
         if cell.targetVolume<=self.Vmax:
            cell.targetVolume+=int(cellDict["growth_timer"])
            cellDict["growth_timer"]=0
      else:
         cellDict["growth_timer"]+=r_grow
         
   def make_mitosis_list(self):
      mitosis_list=[]
      for cell in self.cellList:
         cellDict=CompuCell.getPyAttrib(cell)
         region=cellDict["region"]
         mitosis_probability=self.r_mitosis_list[region]/self.window
         if mitosis_probability>=random():      
            if cell.volume >= self.Vmin_divide:
               mitosis_list.append(cell)
      return mitosis_list
      
   def find_posterior_EN_stripe(self):
      y_EN_pos=9999
      for cell in self.cellList:
         if cell.type==2: # EN cell
            yCM=cell.yCM/float(cell.volume)
            if yCM < y_EN_pos:
               y_EN_pos=yCM
      return y_EN_pos
      
   def find_anterior_EN_stripe(self):
      y_EN_ant=0
      for cell in self.cellList:
         if cell.type==2: # EN cell
            yCM=cell.yCM/float(cell.volume)
            if yCM > y_EN_ant:
               y_EN_ant=yCM
      return y_EN_ant      
   
   def find_y_GZ_mitosis_border(self):
      y_GZ_pos=self.find_posterior_GZ()
      y_GZ_border=y_GZ_pos + self.y_GZ_mitosis_border_percent*(self.y_EN_pos-y_GZ_pos)
      return y_GZ_border
      
   def find_posterior_GZ(self):
      y_GZ_pos=9999
      for cell in self.cellList:
         yCM=cell.yCM/float(cell.volume)
         if yCM < y_GZ_pos:
            y_GZ_pos=yCM
      return y_GZ_pos
      
   # def calculate_t_grow(self,r_mitosis):
      # if r_mitosis > 0:
         # t_cycle=self.window/r_mitosis # approx time to double volume, in MCS
         # t_grow=2*t_cycle/self.V_divide # MCS per pixel growth
      # else:
         # t_grow=999999999
      # return t_grow
      
   def visualizeMitosis(self,cell):
      cellDict=CompuCell.getPyAttrib(cell)
      cellDict['mitosisVisualizationTimer']=self.mitosisVisualizationWindow
      cellDict['returnToCellType']=cell.type
      cell.type = 4 # set to mitosing cell
      
   def mitosisVisualizationCountdown(self):
      for cell in self.cellList:
         if cell.type==4: # if Mitosis cell
            cellDict=CompuCell.getPyAttrib(cell)
            if cellDict['mitosisVisualizationTimer']<=0:
               cell.type=cellDict['returnToCellType']
            else:
               cellDict['mitosisVisualizationTimer']-=1
               
class Measurements(SteppableBasePy):
   def __init__(self,_simulator,_frequency):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        
   def start(self):
      GB_cell_count=self.find_GB_cell_count()
      GZ_cell_count=self.find_GZ_cell_count()
      GB_length=self.find_GB_length()
      GZ_length=self.find_GZ_length()
      GB_area=self.find_GB_area()
      GZ_area=self.find_GZ_area()
      avg_cell_size=self.find_average_cell_size()
      avg_diam=math.sqrt(avg_cell_size)
      
      print '\nGerm band:'
      print 'cell count=' + str(GB_cell_count)
      print 'length=' + str(GB_length) + ' pixels'
      print 'area=' + str(GB_area) + ' pixels'
      print '========='
      print '\nGrowth zone:'
      print 'cell count=' + str(GZ_cell_count)
      print 'length=' + str(GZ_length) + ' pixels'
      print 'area=' + str(GZ_area) + ' pixels'
      print '\nAverage cell size (whole embryo) = ' + str(avg_cell_size) + ' pixels'
      print 'Average cell diameter (whole embryo) = ' + str(avg_diam) + ' pixels' + '\n'
      
   def step(self,mcs):
      GB_cell_count=self.find_GB_cell_count()
      GZ_cell_count=self.find_GZ_cell_count()
      GB_length=self.find_GB_length()
      GZ_length=self.find_GZ_length()
      GB_area=self.find_GB_area()
      GZ_area=self.find_GZ_area()
      avg_cell_size=self.find_average_cell_size()
      avg_diam=math.sqrt(avg_cell_size)
      
      print '\nGerm band:'
      print 'cell count=' + str(GB_cell_count)
      print 'length=' + str(GB_length) + ' pixels'
      print 'area=' + str(GB_area) + ' pixels'
      print '========='
      print '\nGrowth zone:'
      print 'cell count=' + str(GZ_cell_count)
      print 'length=' + str(GZ_length) + ' pixels'
      print 'area=' + str(GZ_area) + ' pixels'
      print '\nAverage cell size (whole embryo) = ' + str(avg_cell_size) + ' pixels'
      print 'Average cell diameter (whole embryo) = ' + str(avg_diam) + ' pixels' + '\n'   
      
   def find_GB_cell_count(self):
      cell_counter=0
      for cell in self.cellList:
         if cell:
            cell_counter+=1
      return cell_counter
      
   def find_GZ_cell_count(self):
      cell_counter=0
      y_EN_pos=self.find_posterior_EN_stripe()
      for cell in self.cellList:
         if cell.yCOM<y_EN_pos:
            cell_counter+=1
      return cell_counter
      
   def find_GB_length(self):
      ant=self.find_anterior_GB()
      pos=self.find_posterior_GB()
      length=ant-pos
      return length
            
   def find_GZ_length(self):
      ant=self.find_posterior_EN_stripe()
      pos=self.find_posterior_GB()
      length=ant-pos
      return length
      
   def find_GB_area(self):
      area=0
      for cell in self.cellList:
         if cell:
            area+=cell.volume
      return area
      
   def find_GZ_area(self):
      area=0
      y_ant=self.find_posterior_EN_stripe()
      for cell in self.cellList:
         if cell.yCOM<y_ant:
            area+=cell.volume
      return area
      
   def find_average_cell_size(self):
      area=self.find_GB_area()
      cell_count=self.find_GB_cell_count()
      avg_cell_volume=area/cell_count
      return avg_cell_volume
            
   def find_posterior_EN_stripe(self):
      y_EN_pos=9999
      for cell in self.cellList:
         if cell.type==2: # EN cell
            yCM=cell.yCOM
            if yCM < y_EN_pos:
               y_EN_pos=yCM
      return y_EN_pos
      
   def find_anterior_GB(self):
      ant=0
      for cell in self.cellList:
         yCM=cell.yCOM
         if yCM>ant:
            ant=yCM
      return ant
      
   def find_posterior_GB(self):
      pos=9999
      for cell in self.cellList:
         yCM=cell.yCOM
         if yCM<pos:
            pos=yCM
      return pos
