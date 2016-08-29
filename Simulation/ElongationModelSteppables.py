from Stats import StatsReporter
from Stats import ParamsContainer
import datetime
from PlayerPython import * 
import CompuCellSetup
from PySteppables import *
from PySteppablesExamples import MitosisSteppableBase
import CompuCell
import sys
import math
from random import random
from copy import deepcopy

class VolumeStabilizer(SteppableBasePy):
    def __init__(self,_simulator,_frequency,_params_container):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.params_container=_params_container

    def start(self):
        Vmin_divide =  self.params_container.getNumberParam('mitosis_Vmin_divide')
        Vmin=int(Vmin_divide/2.0)

        for cell in self.cellList:
            if cell.type==3: # GZ
                volume=int(Vmin+Vmin*random())
                surface=4*int(math.sqrt(volume))
                cell.targetVolume = volume
                cell.targetSurface = surface
            else:
                cell.targetVolume=cell.volume
                cell.targetSurface=cell.surface

            cell.lambdaVolume = 50.0 # A high lambdaVolume makes the cells resist changing volume.
            cell.lambdaSurface = 2.0 # However, a low lambdaSurface still allows them to move easily.
            # In effect, these above two lines allow the cells to travel without squeezing, which would be unrealistic.

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

      

class SarrazinVisualizer(SteppableBasePy):
    def __init__(self, _simulator, _frequency):
        SteppableBasePy.__init__(self, _simulator, _frequency)
        self.vectorCLField = self.createVectorFieldCellLevelPy("Sarrazin_Force")

    def step(self, mcs):
        self.vectorCLField.clear()
        for cell in self.cellList:
            self.vectorCLField[cell] = [cell.lambdaVecX * -1, cell.lambdaVecY * -1, 0]

class Engrailed(SteppableBasePy):
    def __init__(self,_simulator,_frequency,_params_container, _hinder_anterior_cells,_embryo_size):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.hinder_anterior_cells = _hinder_anterior_cells
        self.params_container=_params_container
        self.gene_product_field = None
        self.gene_product_secretor = None
        self.stripe_y = None
        # stripe positioning parameters
        if _embryo_size==1: # sets stripe parameters for small embryo
         self.initial_stripe=805
         self.stripe_width=20
         self.stripe_spacing=50
         self.stripe_period = self.params_container.getNumberParam('stripe_period')
#          self.stripe_period=200
        elif _embryo_size==2:
         self.initial_stripe=1610
         self.stripe_width=30
         self.stripe_spacing=100
         self.stripe_period = self.params_container.getNumberParam('stripe_period')
#          self.stripe_period=400 #400

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
                    if cell.yCOM < self.stripe_y + (self.stripe_width/2+1) and cell.yCOM > self.stripe_y - (self.stripe_width/2+1):
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
      self.r_grow_R0 = self.params_container.getListParam('r_grow_R0')  # [0.0,0.0,0.0]
      self.r_grow_R1 = self.params_container.getListParam('r_grow_R1')  #[0.0,0.0,0.0]
      self.r_grow_R2 = self.params_container.getListParam('r_grow_R2')  #[0.0,0.0,0.0] #0.05 #0
      self.r_grow_R3 = self.params_container.getListParam('r_grow_R3')  #[0.05,0.05,0.05]
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
         cellDict = CompuCell.getPyAttrib(cell)
         cellDict["growth_timer"]=self.attach_growth_timer(cell)  ## attached a countdown timer for cell growth
         cellDict["divided"]=0
         cellDict["divided_GZ"]=0
         cellDict["mitosis_times"]=[]
         cellDict["last_division_mcs"]=0
   
   def step(self,mcs):
      self.mcs=mcs
      #print 'Executing Mitosis Steppable'
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
      parentDict["mitosis_times"].append(self.mcs-parentDict["last_division_mcs"])
      parentDict["last_division_mcs"]=self.mcs
   ### Make a copy of the parent cell's dictionary and attach to child cell   
      for key, item in parentDict.items():
         childDict[key]=deepcopy(parentDict[key])
      childDict["mitosis_times"]=[]
      
    
   
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
               cellDict["divided"]=1
               if cell.type==3: # if GZ cell
                  cellDict["divided_GZ"]=1
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

class RegionalMitosisWithAPConstraint(MitosisSteppableBase):

   def __init__(self,_simulator,_frequency, _params_container, _stats_reporter,_OGPlugin):
      self.reporter = _stats_reporter
      self.params_container = _params_container

      MitosisSteppableBase.__init__(self,_simulator, _frequency)
      self.OGPlugin = _OGPlugin
      self.y_GZ_mitosis_border_percent = self.params_container.getNumberParam('y_GZ_mitosis_border_percent')
      self.transition_times = self.params_container.getListParam('mitosis_transition_times')
  
      self.transition_counter = 0                ## keeps track of which time window simulation is in
      self.r_mitosis_R0 = self.params_container.getListParam('r_mitosis_R0')   # e.g. [0.0, 0.0, 0.0]
      self.r_mitosis_R1 = self.params_container.getListParam('r_mitosis_R1')   # e.g. [0.0, 0.0, 0.0]
      self.r_mitosis_R2 = self.params_container.getListParam('r_mitosis_R2')   # e.g. [0.0, 0.5, 0.0]
      self.r_mitosis_R3 = self.params_container.getListParam('r_mitosis_R3')   # e.g. [0.5, 0.5, 0.5]
           
      # Set r_grow for each region: pixels per MCS added to cell's volume
      self.r_grow_R0 = self.params_container.getListParam('r_grow_R0')  # [0.0,0.0,0.0]
      self.r_grow_R1 = self.params_container.getListParam('r_grow_R1')  #[0.0,0.0,0.0]
      self.r_grow_R2 = self.params_container.getListParam('r_grow_R2')  #[0.0,0.0,0.0] #0.05 #0
      self.r_grow_R3 = self.params_container.getListParam('r_grow_R3')  #[0.05,0.05,0.05]
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
         cellDict["divided"]=0
         cellDict["divided_GZ"]=0
   
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
         
    ##### Attach the elongation constraint to the child cell
      self.OGPlugin.setElongationAxis(childCell, 0, 1) # Here, we define the axis of elongation.
      self.OGPlugin.setConstraintWidth(childCell, 4.0) # And this function gives a width constraint to each cell
      self.OGPlugin.setElongationEnabled(childCell, True) # Make sure to enable or disable elongation in all cells
                                                            # Or unexpected results may occur.
   
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
               cellDict["divided"]=1
               if cell.type==3: # if GZ cell
                  cellDict["divided_GZ"]=1
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
           
class InitializeRegionsWithoutMitosis(MitosisSteppableBase):

   def __init__(self,_simulator,_frequency):
      MitosisSteppableBase.__init__(self,_simulator, _frequency)
      self.y_GZ_mitosis_border_percent = 0    
      
   def start(self):
      self.y_EN_pos=self.find_posterior_EN_stripe()
      self.y_EN_ant=self.find_anterior_EN_stripe()
      self.y_GZ_border=self.find_y_GZ_mitosis_border()
      for cell in self.cellList:
         region=self.assign_cell_region(cell)
         cellDict = CompuCell.getPyAttrib(cell)
         cellDict["divided"]=0
         cellDict["divided_GZ"]=0
   
   def step(self,mcs):

      self.y_EN_pos=self.find_posterior_EN_stripe()
      self.y_EN_ant=self.find_anterior_EN_stripe()
      self.y_GZ_border=self.find_y_GZ_mitosis_border()
      for cell in self.cellList:
         self.assign_cell_region(cell)
   
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
      
# class InitializeRegionsWithoutMitosis(SteppableBasePy):
# 
#    def __init__(self,_simulator,_frequency):
#       SteppableBasePy.__init__(self,_simulator,_frequency)
#       
#    def start(self):
#       self.y_EN_pos=self.find_posterior_EN_stripe()
#       self.y_EN_ant=self.find_anterior_EN_stripe()
#       for cell in self.cellList:
#          region=self.assign_cell_region(cell)
#          cellDict = CompuCell.getPyAttrib(cell)
#          cellDict["divided"]=0
#          cellDict["divided_GZ"]=0
#      
#    def step(self,mcs):
#       self.y_EN_pos=self.find_posterior_EN_stripe()
#       self.y_EN_ant=self.find_anterior_EN_stripe()
#       for cell in self.cellList:
#          self.assign_cell_region(cell)
#      
#    def assign_cell_region(self,cell):
#       yCM=cell.yCOM
#       if yCM > self.y_EN_ant: # if cell is anterior to EN stripes
#          if (cell.type!=4 and cell.type!=2): # if cell is not En or mitosing
#             cell.type=1 # AnteriorLobe
#       elif yCM > self.y_EN_pos: # if cell is in EN-striped region
#          if (cell.type!=2 and cell.type!=4 and cell.type!=1): # if cell is not En or mitosing or AnteriorLobe
#             cell.type=5 # Segmented
#       else:                # if cell is in posterior region of GZ
#          if (cell.type!=2 and cell.type!=4): #if cell is not En or mitosing
#             cell.type=3 # GZ
#                
#    def find_posterior_EN_stripe(self):
#       y_EN_pos=9999
#       for cell in self.cellList:
#          if cell.type==2: # EN cell
#             yCM=cell.yCM/float(cell.volume)
#             if yCM < y_EN_pos:
#                y_EN_pos=yCM
#       return y_EN_pos
#       
#    def find_anterior_EN_stripe(self):
#       y_EN_ant=0
#       for cell in self.cellList:
#          if cell.type==2: # EN cell
#             yCM=cell.yCM/float(cell.volume)
#             if yCM > y_EN_ant:
#                y_EN_ant=yCM
#       return y_EN_ant          
#                
               
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
   def __init__(self,_simulator,_frequency,_x0,_y0,_xf,_yf,_reporter):
      SteppableBasePy.__init__(self,_simulator,_frequency)   
      self.pixelTrackerPlugin=CompuCell.getPixelTrackerPlugin()
      self.x0=_x0; self.xf=_xf
      self.y0=_y0; self.yf=_yf
      self.reporter=_reporter
      
   def setScalarField(self,_field):
      self.dyeField=_field
      
   def start(self):
#       self.reporter.rprint("\nIn the DyeCells module...\n")
      self.zero_field()
      self.zero_cells()
      for i in range(len(self.x0)):
#         self.reporter.rprint('\nfetching dye info...\n')
        dye=1+i
        x0=self.x0[i]
        xf=self.xf[i]
        y0=self.y0[i]
        yf=self.yf[i]
        self.mark_clone(x0,xf,y0,yf,dye)
#       
   def step(self,mcs):
      self.zero_field()
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
                  
   def mark_clone(self,x0,xf,y0,yf,dye):
        for cell in self.cellList:
            if cell:
                cellDict=CompuCell.getPyAttrib(cell)
                xCM=cell.xCOM
                yCM=cell.yCOM
                if (xCM>=x0 and xCM<=xf and yCM>=y0 and yCM<=yf): ## if the cell is within the dye area
#                     self.reporter.rprint('\ndying cell...\n')
                    cellDict["dye"]=dye  ## set initial dye load
                    pixelList=CellPixelList(self.pixelTrackerPlugin,cell)
                    for pixelData in pixelList:
                        pt=pixelData.pixel
                        fillScalarValue(self.dyeField,pt.x,pt.y,pt.z,dye)
                        
   def zero_field(self):
       ##### Set dye field to zero
        for x in range(self.dim.x):
            for y in range(self.dim.y):
                fillScalarValue(self.dyeField,x,y,0,0)
   
   def zero_cells(self):
        for cell in self.cellList:
            if cell:
                cellDict=CompuCell.getPyAttrib(cell)
                cellDict["dye"]=0
               
class DyeMitosisClones(SteppableBasePy):
    def __init__(self,_simulator,_frequency,_window):
        SteppableBasePy.__init__(self,_simulator,_frequency)   
        self.pixelTrackerPlugin=CompuCell.getPixelTrackerPlugin()
        self.window=_window
        
    def setScalarField(self,_field):
        self.dyeField=_field

    def start(self):
    ### Initialize mitosis dye value to zero in all cells
        for cell in self.cellList:
            if cell:
                cellDict=CompuCell.getPyAttrib(cell)
                cellDict["mitosis_dye"]=0
        
    def step(self,mcs):
    ### if within the mitosis dye window, mark mitosing cells (this will depend on the 
    ### visualization of mitosing cells by marking them as type "Mitosing")
        if mcs>=self.window[0] and mcs<=self.window[1]:
            for cell in self.cellList:
                if cell.type==4: # if a type Mitosing cell
                    cellDict=CompuCell.getPyAttrib(cell)
                    cellDict["mitosis_dye"]=1
   
   ##### Set mitosis dye field to zero
        for x in range(self.dim.x):
            for y in range(self.dim.y):
                fillScalarValue(self.dyeField,x,y,0,0)
   ##### identify cells that have mitosis dye and visualize the dye in Player
        for cell in self.cellList:
            if cell:
                cellDict=CompuCell.getPyAttrib(cell)
                dye=cellDict["mitosis_dye"]
                if dye>0:
                    pixelList=CellPixelList(self.pixelTrackerPlugin,cell)
                    for pixelData in pixelList:
                        pt=pixelData.pixel   
                        fillScalarValue(self.dyeField,pt.x,pt.y,pt.z,dye)

class Measurements(SteppableBasePy):
   def __init__(self,_simulator,_frequency, _reporter, _output_path, _batch = False, _batch_iteration = 0):
      SteppableBasePy.__init__(self,_simulator,_frequency)
      self.reporter = _reporter
      self.outp = _output_path
      self.batch = _batch
      self.batch_iteration = _batch_iteration
        
   def start(self):
      try:
          output_folder=self.outp
          stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')
          if not self.batch:
              self.output_filename = output_folder + 'run' + stamp + '.csv'
          else:
              self.output_filename= self.fname = '{}batch_run_{}.csv'.format(output_folder,self.batch_iteration)
          with open(self.output_filename,'w') as self.output_file:
              self.output_file.write('MCS,GB cell count,GB length,GB area,GB cell divisions,GZ cell count,GZ length,GZ area,GZ cell divisions,avg division cycle time\n')
      except IOError:
          raise NameError('Could not output to a csv file properly! Aborting.')
   
      # GB_cell_count=self.find_GB_cell_count()
      # GZ_cell_count=self.find_GZ_cell_count()
      # GB_length=self.find_GB_length()
      # GZ_length=self.find_GZ_length()
      # GB_area=self.find_GB_area()
      # GZ_area=self.find_GZ_area()
      # avg_cell_size=self.find_average_cell_size()
      # avg_diam=math.sqrt(avg_cell_size)
      #
      # self.reporter.rprint('Germ band (pixels): ')
      # self.reporter.printAttrValue(GB_cell_count=GB_cell_count, GB_length=GB_length, GB_area=GB_area)
      # self.reporter.rprint( 'Growth zone (pixels): ')
      # self.reporter.printAttrValue(GZ_cell_count=GZ_cell_count, GZ_length=GZ_length, GZ_area=GZ_area, avg_cell_size=avg_cell_size, avg_diam=avg_diam)
      #
      # print '\nGerm band:'
      # print 'cell count=' + str(GB_cell_count)
      # print 'length=' + str(GB_length) + ' pixels'
      # print 'area=' + str(GB_area) + ' pixels'
      # print '========='
      # print '\nGrowth zone:'
      # print 'cell count=' + str(GZ_cell_count)
      # print 'length=' + str(GZ_length) + ' pixels'
      # print 'area=' + str(GZ_area) + ' pixels'
      # print '\nAverage cell size (whole embryo) = ' + str(avg_cell_size) + ' pixels'
      # print 'Average cell diameter (whole embryo) = ' + str(avg_diam) + ' pixels' + '\n'
      
   def step(self,mcs):
      with open(self.output_filename,'a') as self.output_file:
          GZ_division = self.find_GZ_division_count()
          GB_division = self.find_GB_division_count()
          GB_cell_count = self.find_GB_cell_count()
          GZ_cell_count = self.find_GZ_cell_count()
          GB_length = self.find_GB_length()
          GZ_length = self.find_GZ_length()
          GB_area = self.find_GB_area()
          GZ_area = self.find_GZ_area()
          GZ_normalized_growth = GZ_division / GZ_area
          avg_cell_size = self.find_average_cell_size()
          avg_diam = math.sqrt(avg_cell_size)
          avg_div_time = self.find_avg_div_time()

          measurements_vars = [mcs, GB_cell_count, GB_length, GB_area, GB_division, GZ_cell_count, GZ_length, GZ_area,
                        GZ_division, avg_div_time, GZ_normalized_growth]
          str_rep_measurements_vars = (str(var) for var in measurements_vars)

          self.output_file.write(','.join(str_rep_measurements_vars))
          self.output_file.write('\n')

      # self.output_file=open(self.output_filename,'a')
      # self.output_file.write(str(mcs)+','+str(GB_cell_count)+','+str(GB_length)+','+str(GB_area)+','+str(GB_division)+','+str(GZ_cell_count)+','+str(GZ_length)+','+str(GZ_area)+','+str(GZ_division)+','+str(avg_div_time)+'\n')
      # self.output_file.close()

      # self.reporter.rprint('Germ band (pixels): ')
      # self.reporter.printAttrValue(mcs=mcs, GB_cell_count=GB_cell_count, GB_length=GB_length, GB_area=GB_area)
      # self.reporter.rprint( 'Growth zone (pixels): ')
      # self.reporter.printAttrValue(mcs=mcs,GZ_cell_count=GZ_cell_count, GZ_length=GZ_length, GZ_area=GZ_area, avg_cell_size=avg_cell_size, avg_diam=avg_diam)
      #
      # print '\nGerm band:'
      # print 'cell count=' + str(GB_cell_count)
      # print 'length=' + str(GB_length) + ' pixels'
      # print 'area=' + str(GB_area) + ' pixels'
      # print '========='
      # print '\nGrowth zone:'
      # print 'cell count=' + str(GZ_cell_count)
      # print 'length=' + str(GZ_length) + ' pixels'
      # print 'area=' + str(GZ_area) + ' pixels'
      # print '\nAverage cell size (whole embryo) = ' + str(avg_cell_size) + ' pixels'
      # print 'Average cell diameter (whole embryo) = ' + str(avg_diam) + ' pixels' + '\n'

   def find_avg_div_time(self):
      sum_times=0
      num_times=0
      for cell in self.cellList:
         if cell:
            cellDict=CompuCell.getPyAttrib(cell)
            if "mitosis_times" in cellDict:
                if len(cellDict["mitosis_times"])>1:
                    sum_times+=sum(cellDict["mitosis_times"])-cellDict["mitosis_times"][0]
                    num_times+=len(cellDict["mitosis_times"])-1
      if num_times==0:
         avg_time=0
      else:
         avg_time=sum_times/float(num_times)
      return avg_time
    

   def find_GZ_division_count(self):
      division_count=0
      for cell in self.cellList:
         if cell:
            cellDict=CompuCell.getPyAttrib(cell)
            division_count+=cellDict["divided_GZ"]
            cellDict["divided_GZ"]=0
      return division_count

   def find_GB_division_count(self):
      division_count=0
      for cell in self.cellList:
         if cell:
            cellDict=CompuCell.getPyAttrib(cell)
            division_count+=cellDict["divided"]
            cellDict["divided"]=0
      return division_count
                  
   def find_GB_cell_count(self):
      cell_counter=0
      for cell in self.cellList:
         if cell:
            cell_counter+=1
      return cell_counter
      
   def find_GZ_cell_count(self):
      y_EN_pos=self.find_posterior_EN_stripe()
      return sum(1 for cell in self.cellList if cell.yCOM<y_EN_pos)
      # cell_counter = 0
      # for cell in self.cellList:
      #    if cell.yCOM<y_EN_pos:
      #       cell_counter+=1
      # return cell_counter
      
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
      y_ant=self.find_posterior_EN_stripe()
      area = sum(cell.volume for cell in self.cellList if cell.yCOM < y_ant)
      return area
      # area=0
      # for cell in self.cellList:
      #    if cell.yCOM<y_ant:
      #       area+=cell.volume
      # return area
      
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
