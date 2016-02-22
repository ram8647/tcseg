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
            # print 'cell volume=' + str(cell.volume) + ' cell surface=' + str(cell.surface)

            # This above code prevents the cells from immediately shrinking to nothing.

            cell.lambdaVolume = 50.0 # A high lambdaVolume makes the cells resist changing volume.
            cell.lambdaSurface = 2.0 # However, a low lambdaSurface still allows them to move easily.

            # In effect, these above two lines allow the cells to travel without squeezing, which would be unrealistic.

class SimplifiedForces_GrowthZone(SteppableBasePy):
    def __init__(self,_simulator,_frequency, _params_container, _stats_reporter):
      SteppableBasePy.__init__(self,_simulator,_frequency)
      self.reporter = _stats_reporter
      self.params_container = _params_container
      self.V = self.params_container.getNumberParam('V')
      self.normalized_position = self.params_container.getBooleanParam('position_normalized')

      # Set the constants for the ML force function
      self.k1 = self.params_container.getNumberParam('k1')  # 100.0
      self.k2 = self.params_container.getNumberParam('k2')  # -(1.0/80)
      self.k3 = self.params_container.getNumberParam('k3')  # 0
     
      
      # Set whether force is normalized or based on absolute distance from posterior
      if self.normalized_position:
          self.position = "normalized"  # normalizes position between 0 and 1 to calculate force
      else:
          self.position = "absolute"    # calculates force based on absolute distance from posterior
      
    def start(self):pass

   # Define the AP force function
    def AP_potential_function(self,x,y):
      V = self.V  #50
      return V
      
   # Define the ML force function
    def ML_potential_function(self,x,y):
      if x < self.midline:
         self.k1 = -1 * self.k1
      
      V= self.k1 * math.exp(self.k2 * abs(self.anterior-y)) + self.k3
      return V       
      
    def step(self,mcs):
      self.midline=self.find_midline()
      self.anterior=self.find_anterior_GZ()
      self.posterior=self.find_posterior_GZ()
      for cell in self.cellList:
         if cell.yCOM < self.anterior: # if posterior to last EN stripe
         # if cell.type==3: # GZ
            x=cell.xCOM
            y=cell.yCOM
            V_y=self.AP_potential_function(x,y)
            V_x=self.ML_potential_function(x,y)
            cell.lambdaVecX=V_x
            cell.lambdaVecY=V_y
         else: 
            cell.lambdaVecX=0
            cell.lambdaVecY=0
         # print "cell id: " + str(cell.id) + " cell.COM: " + str(cell.xCOM) + " Vx=" + str(V_x)
         # print "anterior = " +str(self.anterior)
         # print "posterior = " +str(self.posterior)
      
    def find_midline(self):
      x0=999999
      x_max=0
      for cell in self.cellList:
         xCM=cell.xCOM
         if xCM>x_max:
            x_max=xCM
         elif xCM<x0:
            x0=xCM
      midline=x0+0.5*(x_max-x0)
      return midline
      
    def find_anterior_GZ(self):
      y_GZ_ant=0
      for cell in self.cellList:
         if cell.type==3: #GZ
            yCM=cell.yCOM
            if yCM > y_GZ_ant:
               y_GZ_ant=yCM
      return y_GZ_ant    

    def find_posterior_GZ(self):
      y_GZ_pos=999999
      for cell in self.cellList:
         yCM=cell.yCOM
         if yCM < y_GZ_pos:
            y_GZ_pos=yCM
      return y_GZ_pos       

class SimplifiedForces_EntireEmbryo(SteppableBasePy):
    def __init__(self,_simulator,_frequency, _params_container, _stats_reporter):
      SteppableBasePy.__init__(self,_simulator,_frequency)
      self.reporter = _stats_reporter
      self.params_container = _params_container
      self.V = self.params_container.getNumberParam('V')
      self.normalized_position = self.params_container.getBooleanParam('position_normalized')

      # Set the constants for the ML force function
      self.k1 = self.params_container.getNumberParam('k1')  # 100.0
      self.k2 = self.params_container.getNumberParam('k2')  # -(1.0/80)
      self.k3 = self.params_container.getNumberParam('k3')  # 0
      
      # Set whether force is normalized or based on absolute distance from posterior
      if self.normalized_position:
          self.position = "normalized"  # normalizes position between 0 and 1 to calculate force
      else:
          self.position = "absolute"    # calculates force based on absolute distance from posterior
      
    def start(self):pass

   # Define the AP force function
    def AP_potential_function(self,x,y):
      # Set the constants for the AP force function
      V = self.V  #50
      return V
      
   # Define the ML force function
    def ML_potential_function(self,x,y):

      if x < self.midline:
         self.k1 = -1 * self.k1
      
      V = self.k1 * math.exp(self.k2 * abs(self.anterior-y)) + self.k3
      return V       
      
    def step(self,mcs):
      self.midline=self.find_midline()
      self.anterior=self.find_anterior_EN()
      self.posterior=self.find_posterior_GZ()
      for cell in self.cellList:
         if cell.yCOM < self.anterior: # if posterior to first EN stripe
            x=cell.xCOM
            y=cell.yCOM
            V_y=self.AP_potential_function(x,y)
            V_x=self.ML_potential_function(x,y)
            cell.lambdaVecX=V_x
            cell.lambdaVecY=V_y
         else: 
            cell.lambdaVecX=0
            cell.lambdaVecY=0
         # print "cell id: " + str(cell.id) + " cell.COM: " + str(cell.xCOM) + " Vx=" + str(V_x)
         # print "anterior = " +str(self.anterior)
         # print "posterior = " +str(self.posterior)
      
    def find_midline(self):
      x0=999999
      x_max=0
      for cell in self.cellList:
         xCM=cell.xCOM
         if xCM>x_max:
            x_max=xCM
         elif xCM<x0:
            x0=xCM
      midline=x0+0.5*(x_max-x0)
      return midline
      
    def find_anterior_EN(self):
      y_EN_ant=999999
      for cell in self.cellList:
         if cell.type==1: #EN
            yCM=cell.yCOM
            if yCM < y_EN_ant:
               y_EN_ant=yCM
      return y_EN_ant    

    def find_posterior_GZ(self):
      y_GZ_pos=999999
      for cell in self.cellList:
         yCM=cell.yCOM
         if yCM < y_GZ_pos:
            y_GZ_pos=yCM
      return y_GZ_pos       


class SimplifiedForces_SmoothedForces(SteppableBasePy):
    def __init__(self,_simulator,_frequency, _params_container, _stats_reporter):
      SteppableBasePy.__init__(self,_simulator,_frequency)
      self.reporter = _stats_reporter
      self.params_container = _params_container

      # Set the constants for the AP force function
      self.V_AP_GZposterior = self.params_container.getNumberParam('V_AP_GZposterior')
      self.k1_AP_GZanterior = self.params_container.getNumberParam('k1_AP_GZanterior')  
      self.k2_AP_GZanterior = self.params_container.getNumberParam('k2_AP_GZanterior')  
      self.k1_AP_Segments = self.params_container.getNumberParam('k1_AP_Segments')  
      self.k2_AP_Segments = self.params_container.getNumberParam('k2_AP_Segments')
      
      # Set the constants for the ML force function
      self.k1_ML_GZ = self.params_container.getNumberParam('k1_ML_GZ')  
      self.k2_ML_GZ = self.params_container.getNumberParam('k2_ML_GZ')
      self.k1_ML_Segments = self.params_container.getNumberParam('k1_ML_Segments')  
      self.k2_ML_Segments = self.params_container.getNumberParam('k2_ML_Segments')
      
    def start(self):
      self.anterior0=self.find_posterior_EN()
      self.posterior0=self.find_posterior_GZ()
      
    
   # Define the AP force function
    def AP_potential_function(self,mcs,x,y):
      # Set the constants for the AP force function

      if y < self.anterior: # if posterior to first EN stripe
         if (y-self.posterior)/(self.anterior-self.posterior) < 0.5:
            V=self.V_AP_GZposterior # 70
         else:
            k1=self.k1_AP_GZanterior
            k2=self.k2_AP_GZanterior
              
            V=k1/0.5*((self.anterior-y)/(self.anterior-self.posterior))+k2
         
      else:
         k1=self.k1_AP_Segments
         k2=self.k2_AP_Segments
         V=k1*math.exp(k2*abs((y-self.anterior)))
      return V
      
   # Define the ML force function
    def ML_potential_function(self,mcs,x,y):
      # Set the constants for the ML force function
      if y < self.anterior: # if posterior to first EN stripe
         k1=self.k1_ML_GZ
         k2=self.k2_ML_GZ
      else:
         k1=self.k1_ML_Segments
         k2=self.k2_ML_Segments         
            
      if x<self.midline:
         k1=-1*k1
      
      V=k1*math.exp(k2*abs(self.anterior-y))
      # V=0
      return V       
      
    def step(self,mcs):
      self.midline=self.find_midline()
      self.anterior=self.find_posterior_EN()
      self.posterior=self.find_posterior_GZ()
      for cell in self.cellList:
         x=cell.xCOM
         y=cell.yCOM
         V_y=self.AP_potential_function(mcs,x,y)
         V_x=self.ML_potential_function(mcs,x,y)
         cell.lambdaVecX=V_x
         cell.lambdaVecY=V_y

      
    def find_midline(self):
      x0=999999
      x_max=0
      for cell in self.cellList:
         xCM=cell.xCOM
         if xCM>x_max:
            x_max=xCM
         elif xCM<x0:
            x0=xCM
      midline=x0+0.5*(x_max-x0)
      return midline
      
    def find_posterior_EN(self):
      y_EN_pos=999999
      for cell in self.cellList:
         if cell.type==2: #Anterior
            yCM=cell.yCOM
            if yCM < y_EN_pos:
               y_EN_pos=yCM
      return y_EN_pos    

    def find_posterior_GZ(self):
      y_GZ_pos=999999
      for cell in self.cellList:
         yCM=cell.yCOM
         if yCM < y_GZ_pos:
            y_GZ_pos=yCM
      return y_GZ_pos       

      
class AssignCellAddresses(SteppableBasePy): # this steppable assigns each cell an address along the AP axis
    def __init__(self,_simulator,_frequency, _reporter):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.reporter = _reporter

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
#        self.reporter.rprint("self.anteriormost_cell_y: ", self.anteriormost_cell_y)

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
        if cell.type==1: # AnteriorLobe
        # if address < 0.2:
            cell.lambdaSurface += (0.2 - address) * 100

    def start(self): self.assignAllRelativeAddresses()
    def step(self,mcs): self.assignAllRelativeAddresses()

class SarrazinVisualizer(SteppableBasePy):
    def __init__(self, _simulator, _frequency):
        SteppableBasePy.__init__(self, _simulator, _frequency)
        self.vectorCLField = self.createVectorFieldCellLevelPy("Sarrazin_Force")

    def step(self, mcs):
        self.vectorCLField.clear()
        for cell in self.cellList:
            self.vectorCLField[cell] = [cell.lambdaVecX * -1, cell.lambdaVecY * -1, 0]

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
        # stripe positioning parameters
        self.initial_stripe=805
        self.stripe_width=10
        self.stripe_period=300
        self.stripe_spacing=50

    def start(self):
        if self.hinder_anterior_cells == True:
            self.gene_product_field = CompuCell.getConcentrationField(self.simulator,"EN_GENE_PRODUCT")
            self.gene_product_secretor = self.getFieldSecretor("EN_GENE_PRODUCT")
        for cell in self.cellList: # THIS BLOCK HAS BEEN JUSTIFIED OUTSIDE OF EARLIER "IF" STATEMENT (sdh)
            self.stripe_y = self.initial_stripe 
            if cell.yCOM < self.stripe_y+self.stripe_width/2 and cell.yCOM > self.stripe_y-self.stripe_width/2:
            # cellDict["En_ON"] = True
                cell.type = 2 # EN cell
                if self.hinder_anterior_cells == True:
                     self.gene_product_secretor.secreteInsideCell(cell, 1)

    def step(self, mcs):
        if (mcs != 0) and (mcs % self.stripe_period == 0) :
            self.stripe_y -= self.stripe_spacing
            #### SarrazinForces.setstripe_y(SarrazinForces, self.stripe_y)
            for cell in self.cellList:
                ####cellDict = CompuCell.getPyAttrib(cell)
                ##### print "self.stripe_y:    ", self.stripe_y
                ##### if cell.type == 1: #AnteriorLobe

                if cell:
                    if cell.yCOM < self.stripe_y + (self.stripe_width+1) and cell.yCOM > self.stripe_y - (self.stripe_width+1):
                        ######cellDict["En_ON"] = True
                        cell.type = 2 # EN
                        #####if self.hinder_anterior_cells == True:
                            #######self.gene_product_secretor.secreteInsideCell(cell,1)

            
class RegionalMitosis(MitosisSteppableBase):

   def __init__(self,_simulator,_frequency, _params_container, _stats_reporter):
      self.reporter = _stats_reporter
      self.params_container = _params_container

      MitosisSteppableBase.__init__(self,_simulator, _frequency)
      self.y_GZ_mitosis_border_percent = self.params_container.getNumberParam('y_GZ_mitosis_border_percent')
      self.transition_times = self.params_container.getListParam('mitosis_transition_times')
  
      self.transition_counter = 0                ## keeps track of which time window simulation is in
      self.r_mitosis_R0 = self.params_container.getListParam('r_mitosis_R0')   # e.g. [0.0, 0.0, 0.0]
      self.r_mitosis_R1 = self.params_container.getListParam('r_mitosis_R1')   # e.g. [0.0, 0.0, 0.0]
      self.r_mitosis_R2 = self.params_container.getListParam('r_mitosis_R2')   # e.g. [0.0, 0.5, 0.0]
      self.r_mitosis_R3 = self.params_container.getListParam('r_mitosis_R3')   # e.g. [0.5, 0.5, 0.5]
           
      # Set r_grow for each region: pixels per MCS added to cell's volume
      self.r_grow_R0 = self.r_mitosis_R0  # [0.0,0.0,0.0]
      self.r_grow_R1 = self.r_mitosis_R1  #[0.0,0.0,0.0]
      self.r_grow_R2 = self.r_mitosis_R2  #[0.0,0.0,0.0] #0.05 #0
      self.r_grow_R3 = self.r_mitosis_R3  #[0.05,0.05,0.05]
      self.r_grow_list=[self.r_grow_R0[0],self.r_grow_R1[0],self.r_grow_R2[0],self.r_grow_R3[0]]      
      
      self.fraction_AP_oriented = self.params_container.getNumberParam('mitosis_fraction_AP_oriented') # 0 #0.5
      
      self.window = self.params_container.getNumberParam('mitosis_window') # 500 
      self.Vmin_divide =  self.params_container.getNumberParam('mitosis_Vmin_divide') # 60 
      self.Vmax = self.params_container.getNumberParam('mitosis_Vmax')    # 90 
      self.mitosisVisualizationFlag = self.params_container.getNumberParam('mitosis_visualization_flag')     # 1 
      self.mitosisVisualizationWindow = self.params_container.getNumberParam('mitosis_visualization_window') # 100
      
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
      if mcs in self.transition_times:
         print '*******************TRANSITIONING MITOSIS TIME WINDOW**********************'
         self.reporter.printLn( '*******************TRANSITIONING MITOSIS TIME WINDOW**********************')
         self.r_mitosis_list=[self.r_mitosis_R0[self.transition_counter],self.r_mitosis_R1[self.transition_counter],self.r_mitosis_R2[self.transition_counter],self.r_mitosis_R3[self.transition_counter]]
         self.r_grow_list=[self.r_grow_R0[self.transition_counter],self.r_grow_R1[self.transition_counter],self.r_grow_R2[self.transition_counter],self.r_grow_R3[self.transition_counter]]      
         self.transition_counter+=1

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
         if (cell.type!=4 and cell.type!=2): # if cell is not En or mitosing
            cell.type=1 # AnteriorLobe
      elif yCM > self.y_EN_pos: # if cell is in EN-striped region
         cellDict["region"]=1
         if (cell.type!=2 and cell.type!=4 and cell.type!=1): # if cell is not En or mitosing or AnteriorLobe
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

### Constrains a subpopulation of cells to grow along a particular axis by biasing the 
### addition of new pixels and constraining the width of cells orthogonal to the axis of growth 
### Developed by Jeremy Fisher (2015)              
class OrientedConstraintSteppable(SteppableBasePy):
   def __init__(self,_simulator,_frequency,_OGPlugin):
      SteppableBasePy.__init__(self,_simulator,_frequency)
      self.OGPlugin = _OGPlugin
        
   def start(self):
      for cell in self.cellList:
         if cell:
            #### cell.lambdaVolume=2.0
            cell.targetVolume=cell.volume
            
            #### self.OGPlugin.setElongationAxis(cell, math.cos(math.pi / 3), math.sin(math.pi / 3)) # Here, we define the axis of elongatino.
            self.OGPlugin.setElongationAxis(cell, 0, 1) # Here, we define the axis of elongation.
            self.OGPlugin.setConstraintWidth(cell, 4.0) # And this function gives a width constraint to each cell
            self.OGPlugin.setElongationEnabled(cell, True) # Make sure to enable or disable elongation in all cells
                                                            # Or unexpected results may occur.

               
## Labels a population of cells and outputs to a Player visualization field   
class DyeCells(SteppableBasePy):
   def __init__(self,_simulator,_frequency,_x0,_y0,_xf,_yf):
      SteppableBasePy.__init__(self,_simulator,_frequency)   
      self.pixelTrackerPlugin=CompuCell.getPixelTrackerPlugin()
      self.x0=_x0; self.xf=_xf
      self.y0=_y0; self.yf=_yf
      
   def setScalarField(self,_field):
      self.dyeField=_field
      
   def start(self):
   ## TEST
      # dye=1
      # for cell in self.cellList:
         # if cell:
            # pixelList=CellPixelList(self.pixelTrackerPlugin,cell)
            # for pixelData in pixelList:
               # pt=pixelData.pixel   
               # fillScalarValue(self.dyeField,pt.x,pt.y,pt.z,dye)   
   
      ## set dye load as an item in cells' dictionaries
      dye=1   # magnitude of initial dye load (1)
      for cell in self.cellList:
         if cell:
            cellDict=CompuCell.getPyAttrib(cell)
            xCM=cell.xCOM
            yCM=cell.yCOM
            if (xCM>=self.x0 and xCM<=self.xf and yCM>=self.y0 and yCM<=self.yf): ## if the cell is within the dye area
               cellDict["dye"]=dye  ## set initial dye load
               pixelList=CellPixelList(self.pixelTrackerPlugin,cell)
               for pixelData in pixelList:
                  pt=pixelData.pixel
                  fillScalarValue(self.dyeField,pt.x,pt.y,pt.z,dye)
            else:
               cellDict["dye"]=0  ## set initial dye load to 0
      
   def step(self,mcs):
   ##### Set dye field to zero
      for x in range(self.dim.x):
         for y in range(self.dim.y):
            fillScalarValue(self.dyeField,x,y,0,0)
   ##### identify cells that have dye and visualize the dye in Player
      for cell in self.cellList:
         if cell:
            cellDict=CompuCell.getPyAttrib(cell)
            dye=cellDict["dye"]
            if dye>0:
               pixelList=CellPixelList(self.pixelTrackerPlugin,cell)
               for pixelData in pixelList:
                  pt=pixelData.pixel   
                  fillScalarValue(self.dyeField,pt.x,pt.y,pt.z,dye)
               

class Measurements(SteppableBasePy):
   def __init__(self,_simulator,_frequency, _reporter):
      SteppableBasePy.__init__(self,_simulator,_frequency)
      self.reporter = _reporter
        
   def start(self):
      GB_cell_count=self.find_GB_cell_count()
      GZ_cell_count=self.find_GZ_cell_count()
      GB_length=self.find_GB_length()
      GZ_length=self.find_GZ_length()
      GB_area=self.find_GB_area()
      GZ_area=self.find_GZ_area()
      avg_cell_size=self.find_average_cell_size()
      avg_diam=math.sqrt(avg_cell_size)
      
      self.reporter.rprint('Germ band (pixels): ')
      self.reporter.printAttrValue(GB_cell_count=GB_cell_count, GB_length=GB_length, GB_area=GB_area)
      self.reporter.rprint( 'Growth zone (pixels): ')
      self.reporter.printAttrValue(GZ_cell_count=GZ_cell_count, GZ_length=GZ_length, GZ_area=GZ_area, avg_cell_size=avg_cell_size, avg_diam=avg_diam)

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
      
      self.reporter.rprint('Germ band (pixels): ')
      self.reporter.printAttrValue(mcs=mcs, GB_cell_count=GB_cell_count, GB_length=GB_length, GB_area=GB_area)
      self.reporter.rprint( 'Growth zone (pixels): ')
      self.reporter.printAttrValue(mcs=mcs,GZ_cell_count=GZ_cell_count, GZ_length=GZ_length, GZ_area=GZ_area, avg_cell_size=avg_cell_size, avg_diam=avg_diam)

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
