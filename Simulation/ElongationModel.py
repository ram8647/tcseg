from PlayerPython import * 
import CompuCellSetup

# Parameter container, instantiated below in configureSimulation()
global params_container

# Simulation Dimension Parameters
global Dx; global Dy

# General simulation flags
global batch; global speed_up_sim

## Mitosis parameters
global regional_mitosis_flag; global y_GZ_mitosis_border

# Cell labeling parameters
global dye_flag 

def configureSimulation(sim):
    import CompuCellSetup
    from XMLUtils import ElementCC3D

    ## ********** Import Some Parameters Here ************** ##
    print '>>>>>>>>>>>>>>>> Before imports >>>>>>>>>>>>>>>>'
    print 'Current directory', os.getcwd()

    from Stats import ParamsContainer, StatsReporter
    global reporter; reporter = StatsReporter('../tcseg/Simulation/runs/')
    global params_container; params_container = ParamsContainer(reporter)
    
    ##  ********* Dictionary that stores the parameters   ********** ##
    params_dict = params_container.inputParamsFromFile('params', folder='../tcseg/Simulation/')

    global Dx; Dx = params_container.getNumberParam('Dx')
    global Dy; Dy = params_container.getNumberParam('Dy')
    global dye_flag; dye_flag = params_container.getNumberParam('dye_flag')
    global speed_up_sim; speed_up_sim = params_container.getBooleanParam('speed_up_sim')
    global batch; batch = params_container.getBooleanParam('batch')
    global hinder_cells_near_EN; hinder_cells_near_EN = params_container.getBooleanParam('hinder_cells_near_EN')
    global regional_mitosis_flag; regional_mitosis_flag = params_container.getNumberParam('regional_mitosis_flag')

    print '>>>>>>>>>>>>>>>> After imports >>>>>>>>>>>>>>>>'
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
    SteppableElmnt.ElementCC3D("PIFName",{},"Simulation/InitialConditions_3_19_2015.piff")

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

## Import custom classes here

from  ElongationModelSteppables import jeremyVector
from  ElongationModelSteppables import EN_stripe

## ***** Create Steppable Instances  ***** ##

from ElongationModelSteppables import VolumeStabilizer
s1 = VolumeStabilizer(sim,_frequency = 1)

from ElongationModelSteppables import AssignCellAddresses
s2 = AssignCellAddresses(sim,_frequency = 1, _reporter = reporter)

from ElongationModelSteppables import Measurements
s4 = Measurements(sim,_frequency = 100, _reporter=reporter)

# EN_stripe parameters
# The speeds and positions come from Brown et all, 1994. I measured the relative position of each stripe in ImageJ
# and found that they move up ~ 6% of the relative body length in the period of interest. 90 is the number
# of times this steppable is called during the simulation. So the speed is 6% body length / 90 steps, or 0.06/90 that is 0.0007.

from ElongationModelSteppables import Engrailed
s5 = Engrailed(sim, _frequency = 1,
                      _stripes = [EN_stripe(_relative_position = 0.25, _speed_mcs = 0.0007, _start_mcs = 0)], # stripe 0.
                                  #EN_stripe(_relative_position = 0.35, _speed_mcs = 0.0007, _start_mcs = 0), # stripe 1
                                  #EN_stripe(_relative_position = 0.45, _speed_mcs = 0.0007, _start_mcs = 0)], # stripe 2
                      _hinder_anterior_cells = hinder_cells_near_EN, height = s2.height)

# The speeds and positions come from Brown et all, 1994. I measured the relative position of each stripe in ImageJ
# and found that they move up ~ 6% of the relative body length in the period of interest. 90 is the number
# of times this steppable is called during the simulation. So the speed is 6% body length / 90 steps, or 0.06/90 that is 0.0007.


## *****  Add steppables to the model **********  ##
steppables = [s1,s2,s4,s5]
for steppable in steppables: steppableRegistry.registerSteppable(steppable)

## ***** Register the Mitosis Steppable
if regional_mitosis_flag:
   from ElongationModelSteppables import RegionalMitosis
   mitosis = RegionalMitosis(sim,_frequency = 1, _params_container = params_container, _stats_reporter = reporter)
   steppableRegistry.registerSteppable(mitosis)

##  Register one of the Simplified Forces Steppables
simplified_forces_flag = params_container.getNumberParam('simplified_forces_flag')
if simplified_forces_flag != 0:
   if simplified_forces_flag == 1:
      from ElongationModelSteppables import SimplifiedForces_GrowthZone
      simplified_forces = SimplifiedForces_GrowthZone(sim,_frequency = 10, _params_container = params_container, _stats_reporter = reporter)
   else:
      from ElongationModelSteppables import SimplifiedForces_EntireEmbryo
      simplified_forces = SimplifiedForces_EntireEmbryo(sim,_frequency = 10, _params_container = params_container, _stats_reporter = reporter)
   steppableRegistry.registerSteppable(simplified_forces)

###  s3 = SimplifiedForces_GrowthZone(sim,_frequency = 10, _params_container = params_container, _stats_reporter = reporter)


###### Add extra player fields here
if dye_flag:
   dim=sim.getPotts().getCellFieldG().getDim()
   Label01Field=simthread.createFloatFieldPy(dim,"CellLabel01")
  #### Label02Field=simthread.createFloatFieldPy(dim,"CellLabel02")
  #### Label03Field=simthread.createFloatFieldPy(dim,"CellLabel03")   

if dye_flag:
   from ElongationModelSteppables import DyeCells
   dyeCells=DyeCells(_simulator=sim,_frequency=20,
#     _x0=x0_dye,_y0=y0_dye,_xf=xf_dye,_yf=yf_dye)
     _x0 = params_container.getNumberParam('x0_dye'),
     _y0 = params_container.getNumberParam('y0_dye'),
     _xf = params_container.getNumberParam('xf_dye'),
     _yf = params_container.getNumberParam('yf_dye'))
   dyeCells.setScalarField(Label01Field)
   steppableRegistry.registerSteppable(dyeCells) 

##  ****  Start the Simulation  *****  ##
CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
        
