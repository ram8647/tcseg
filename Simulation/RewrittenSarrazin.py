from PlayerPython import * 
import CompuCellSetup
##******** Simulation Flags ********##

# Simulation Dimension Parameters
global Dx; global Dy

# general simulation flags
global batch; global speed_up_sim

# sarrazin force flags
global y_target_offset; global pull_force_magnitude; global pinch_force_relative_center
global pinch_force_mag; global pinch_force_falloff_sharpness

global hinder_cells_near_EN
global stripe_y

## Mitosis parameters
global regional_mitosis; global y_GZ_mitosis_border

##  Set Simulation Dimension Parameters  ##
Dx = 320
Dy = 750 #480

##******** Configure Simulation Flags ********##

speed_up_sim = False
batch = False
hinder_cells_near_EN = False  ## THIS PARAMETER IS CURRENTLY NOT DOING ANYTHING MECHANISTIC (sdh)

## configure the sarrazin force steppable. Comments show default values.

y_target_offset = 15 # 15
pull_force_magnitude = 60 #60
pinch_force_relative_center = 0.35 #0.35
pinch_force_mag = 30 #17
pinch_force_falloff_sharpness = 3.5 #3.5

## Set Mitosis flag ##
regional_mitosis=1 # RegionalMitosis steppable runs if nonzero
## Set Mitosis Steppable parameters in Steppables file ##

##******** Batch Run Configuration ********##

if batch == True:
    speed_up_sim = True
    file = open("variables.txt", "r") # note, this should be relative to the location command from which the CC3D program was opened
    i1, i2 = [float(i) for i in file.readlines()[0:2]] # this loads in a document with each variable to a line, in the order as seen on the left

def configureSimulation(sim):
    import CompuCellSetup
    from XMLUtils import ElementCC3D
    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"20140724","Version":"3.7.2"})
    PottsElmnt=CompuCell3DElmnt.ElementCC3D("Potts")
    
    # Basic properties of CPM (GGH) algorithm
    PottsElmnt.ElementCC3D("Dimensions",{"x":Dx,"y":Dy,"z":1})
    PottsElmnt.ElementCC3D("Steps",{},"3001")
    PottsElmnt.ElementCC3D("Temperature",{},"10.0")
    PottsElmnt.ElementCC3D("NeighborOrder",{},"1")
    
    PluginElmnt=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CellType"}) # Listing all cell types in the simulation
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"0","TypeName":"Medium"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"1","TypeName":"AnteriorLobe"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"2","TypeName":"EN"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"3","TypeName":"GZ"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"4","TypeName":"Mitosing"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"5","TypeName":"Segmented"})
    
    PluginElmnt_1=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Volume"}) # Cell property trackers and manipulators
    PluginElmnt_2=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Surface"})
    extPotential=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"ExternalPotential"})
    PluginElmnt_4=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CenterOfMass"})
    PluginElmnt_6=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"NeighborTracker"})
    PluginElmnt_6=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Secretion"})
    
    PluginElmnt_5=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Contact"}) # Specification of adhesion energies
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Medium"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"AnteriorLobe"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"EN"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"GZ"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Mitosing"},"100.0")    
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Segmented"},"100.0")    
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"AnteriorLobe"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"EN"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"GZ"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"Mitosing"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"Segmented"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"EN","Type2":"EN"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"EN","Type2":"GZ"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"EN","Type2":"Mitosing"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"EN","Type2":"Segmented"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"GZ","Type2":"GZ"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"GZ","Type2":"Mitosing"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"GZ","Type2":"Segmented"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Mitosing","Type2":"Mitosing"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Mitosing","Type2":"Segmented"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Segmented","Type2":"Segmented"},"10.0")
    PluginElmnt_5.ElementCC3D("NeighborOrder",{},"1")

    
    ## EN GENE PRODUCT FIELD NOT ACCOMPLISHING ANYTHING MECHANISTIC, AND SLOWING DOWN SIMULATION A LOT
    ## ***** Define the properties of the Engrailed gene product ***** ##

    if hinder_cells_near_EN: # THIS IS TO AVOID SLOWDOWN WHEN FIELD NOT NECESSARY (sdh)
      SteppableElmnt=CompuCell3DElmnt.ElementCC3D("Steppable",{"Type":"DiffusionSolverFE"})
      DiffusionFieldElmnt=SteppableElmnt.ElementCC3D("DiffusionField",{"Name":"EN_GENE_PRODUCT"})
      DiffusionDataElmnt=DiffusionFieldElmnt.ElementCC3D("DiffusionData")
      DiffusionDataElmnt.ElementCC3D("FieldName",{},"EN_GENE_PRODUCT")
      DiffusionDataElmnt.ElementCC3D("GlobalDiffusionConstant",{},"10.0") # 0.05 for anterior retardation; 0.5 for bidirectional retardation
      DiffusionDataElmnt.ElementCC3D("GlobalDecayConstant",{},"0.05") # 0.005 for anterior retardation; 0.05 for bidirectional retardation

    ## ***** ##
    
    SteppableElmnt=CompuCell3DElmnt.ElementCC3D("Steppable",{"Type":"PIFInitializer"})
    
    # Initial layout of cells using PIFF file. Piff files can be generated using PIFGEnerator
    SteppableElmnt.ElementCC3D("PIFName",{},"Simulation/Dec2014_v02.piff")

    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)
            
import sys
from os import environ
from os import getcwd
import string


sys.path.append(environ["PYTHON_MODULE_PATH"])

##******** Configure Simulation Flags ********##

import CompuCellSetup
sim,simthread = CompuCellSetup.getCoreSimulationObjects()
configureSimulation(sim)
CompuCellSetup.initializeSimulationObjects(sim,simthread)
steppableRegistry=CompuCellSetup.getSteppableRegistry()

## import my custom classes here

from  RewrittenSarrazinSteppables import jeremyVector
from  RewrittenSarrazinSteppables import EN_stripe

## ***** Declare Steppables Here ***** ##

from RewrittenSarrazinSteppables import VolumeStabilizer
s1 = VolumeStabilizer(sim,_frequency = 1)

from RewrittenSarrazinSteppables import AssignCellAddresses
s2 = AssignCellAddresses(sim,_frequency = 1)


from RewrittenSarrazinSteppables import SimplifiedForces
s3 = SimplifiedForces(sim,_frequency = 10)


# from RewrittenSarrazinSteppables import SarrazinForces
# s3 = SarrazinForces(sim,_frequency = 1, _y_target_offset = y_target_offset, _pull_force_magnitude = pull_force_magnitude,
#                       _pinch_force_relative_center = pinch_force_relative_center, _pinch_force_mag = pinch_force_mag,
#                       _pinch_force_falloff_sharpness = pinch_force_falloff_sharpness)

#from RewrittenSarrazinSteppables import lobePincher
#s4 = lobePincher(sim, _frequency = 10, _center_x = 152, _center_y = 35, _extent = 9)

from RewrittenSarrazinSteppables import Engrailed
s5 = Engrailed(sim, _frequency = 1,
                      _stripes = [EN_stripe(_relative_position = 0.25, _speed_mcs = 0.0007, _start_mcs = 0)], # stripe 0.
                                  #EN_stripe(_relative_position = 0.35, _speed_mcs = 0.0007, _start_mcs = 0), # stripe 1
                                  #EN_stripe(_relative_position = 0.45, _speed_mcs = 0.0007, _start_mcs = 0)], # stripe 2
                      _hinder_anterior_cells = hinder_cells_near_EN, height = s2.height)

# The speeds and positions come from Brown et all, 1994. I measured the relative position of each stripe in ImageJ
# and found that they move up ~ 6% of the relative body length in the period of interest. 90 is the number
# of times this steppable is called during the simulation. So the speed is 6% body length / 90 steps, or 0.06/90 that is 0.0007.


steppables = [s1,s2,s3,s5]
for steppable in steppables: steppableRegistry.registerSteppable(steppable)

## ***** Declare the other steppables *****  ##
if regional_mitosis:
   from RewrittenSarrazinSteppables import RegionalMitosis
   mitosis = RegionalMitosis(sim,_frequency = 1)
   steppableRegistry.registerSteppable(mitosis)

'''
if speed_up_sim == False: # Disable the superfluous code for runs where efficiency is important
    from RewrittenSarrazinSteppables import SarrazinVisualizer
    SV = SarrazinVisualizer(sim, _frequency = 1)

    from RewrittenSarrazinSteppables import SarrazinCloneVisualizer
    SCV = SarrazinCloneVisualizer(sim, _frequency = 1, _cell_locs =  [jeremyVector(_x = 160, _y = 275),
                                                  jeremyVector(_x = 120, _y = 250),
                                                  jeremyVector(_x = 113, _y = 240),
                                                  jeremyVector(_x = 106, _y = 210),
                                                  jeremyVector(_x = 210, _y = 250),
                                                  jeremyVector(_x = 207, _y = 240),
                                                  jeremyVector(_x = 214, _y = 210)])

    super_steppables = [SV, SCV]
    for steppable in super_steppables: steppableRegistry.registerSteppable(steppable)
'''

CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
        
