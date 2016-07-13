from PlayerPython import * 
import CompuCellSetup

# Parameter container, instantiated below in configureSimulation()
global params_container

# Simulation Dimension Parameters
global Dx; global Dy

# General simulation flags
global batch; global speed_up_sim

# Mitosis parameters
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
    global reporter; reporter = StatsReporter('/Applications/CC3D_3.7.5_new/Simulations/tcseg/Stats_Output/')
    global params_container; params_container = ParamsContainer(reporter)


    ##  ********* Dictionary that stores the parameters   ********** ##
    params_dict = params_container.inputParamsFromFile('params', folder='/Applications/CC3D_3.7.5_new/Simulations/tcseg/Simulation/')

    global embryo_size; embryo_size = params_container.getNumberParam('embryo_size')
    global Dx; global Dy
    if embryo_size==1:
        Dx = 320
        Dy = 910
    elif embryo_size==2:
        Dx = 450
#         Dx = 900
        Dy = 1800
    global dye_flag; dye_flag = params_container.getNumberParam('dye_flag')
#     global speed_up_sim; speed_up_sim = params_container.getBooleanParam('speed_up_sim')
#     global batch; batch = params_container.getBooleanParam('batch')
#     global hinder_cells_near_EN; hinder_cells_near_EN = params_container.getBooleanParam('hinder_cells_near_EN')
    global speed_up_sim; speed_up_sim=False
    global batch; batch=False
    global hinder_cells_near_EN; hinder_cells_near_EN=False
    global AP_growth_constraint_flag; AP_growth_constraint_flag = params_container.getNumberParam('AP_growth_constraint_flag')
    global dye_mitosis_clones; dye_mitosis_clones=params_container.getNumberParam('dye_mitosis_clones')
    global mitosis_dye_window; mitosis_dye_window=params_container.getListParam('mitosis_dye_window')
    
    print '>>>>>>>>>>>>>>>> After imports >>>>>>>>>>>>>>>>'
    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"20140724","Version":"3.7.2"})
    PottsElmnt=CompuCell3DElmnt.ElementCC3D("Potts")
    
    # Basic properties of CPM (GGH) algorithm
    PottsElmnt.ElementCC3D("Dimensions",{"x":Dx,"y":Dy,"z":1})
    PottsElmnt.ElementCC3D("Steps",{},"3601")
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
    PluginElmnt_7=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Secretion"})
    if AP_growth_constraint_flag:
        PluginElmnt_8=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"OrientedGrowth"})
        PluginElmnt_8.ElementCC3D("Penalty",{},9999)
        PluginElmnt_8.ElementCC3D("Falloff",{},2)
    
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
    if embryo_size==1:
        SteppableElmnt.ElementCC3D("PIFName",{},"Simulation/InitialConditions_3_19_2015.piff")
    elif embryo_size==2:
        SteppableElmnt.ElementCC3D("PIFName",{},"Simulation/InitialConditions_04_06_2015.piff")
#         SteppableElmnt.ElementCC3D("PIFName",{},"Simulation/InitialConditions_05_01_2016_straight.piff")

    
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

## ***** Create Steppable Instances  ***** ##

from ElongationModelSteppables import VolumeStabilizer
s1 = VolumeStabilizer(sim,_frequency = 1)

if AP_growth_constraint_flag:
    OrientedGrowthPlugin = CompuCell.getOrientedGrowthPlugin()
    from ElongationModelSteppables import OrientedConstraintSteppable
    OrientedConstraintSteppableInstance=OrientedConstraintSteppable(sim,_frequency=1,_OGPlugin=OrientedGrowthPlugin)
    steppableRegistry.registerSteppable(OrientedConstraintSteppableInstance)

from ElongationModelSteppables import Measurements
s4 = Measurements(sim,_frequency = 100, _reporter=reporter)

# EN_stripe parameters
# The speeds and positions come from Brown et all, 1994. I measured the relative position of each stripe in ImageJ
# and found that they move up ~ 6% of the relative body length in the period of interest. 90 is the number
# of times this steppable is called during the simulation. So the speed is 6% body length / 90 steps, or 0.06/90 that is 0.0007.

from ElongationModelSteppables import Engrailed
s5 = Engrailed(sim, _frequency = 1,_params_container = params_container,_hinder_anterior_cells = hinder_cells_near_EN,_embryo_size=embryo_size)

# The speeds and positions come from Brown et all, 1994. I measured the relative position of each stripe in ImageJ
# and found that they move up ~ 6% of the relative body length in the period of interest. 90 is the number
# of times this steppable is called during the simulation. So the speed is 6% body length / 90 steps, or 0.06/90 that is 0.0007.


## *****  Add steppables to the model **********  ##
steppables = [s1,s4,s5]
# steppables = [s1,s5]
for steppable in steppables: steppableRegistry.registerSteppable(steppable)

## ***** Register the Mitosis Steppable
mitosis_on=params_container.getNumberParam('mitosis_on')

if mitosis_on==0:
    from ElongationModelSteppables import InitializeRegionsWithoutMitosis
    mitosis = InitializeRegionsWithoutMitosis(sim,_frequency=1)
    steppableRegistry.registerSteppable(mitosis)
elif AP_growth_constraint_flag:
    from ElongationModelSteppables import RegionalMitosisWithAPConstraint
    mitosis = RegionalMitosisWithAPConstraint(sim,_frequency = 1, _params_container = params_container, _stats_reporter = reporter,_OGPlugin=OrientedGrowthPlugin)
    steppableRegistry.registerSteppable(mitosis)
else:
    from ElongationModelSteppables import RegionalMitosis
    mitosis = RegionalMitosis(sim,_frequency = 1, _params_container = params_container, _stats_reporter = reporter)
    steppableRegistry.registerSteppable(mitosis)    

if params_container.getNumberParam('forces_on'):
##  Register the Simplified Forces Steppable
    from ElongationModelSteppables import SimplifiedForces_SmoothedForces
    simplified_forces = SimplifiedForces_SmoothedForces(sim,_frequency = 10, _params_container = params_container, _stats_reporter = reporter)  
    steppableRegistry.registerSteppable(simplified_forces)

###### Add extra player fields here
if dye_flag:
    dim=sim.getPotts().getCellFieldG().getDim()
    Label01Field=simthread.createFloatFieldPy(dim,"CellLabel01")
if dye_mitosis_clones:
    dim=sim.getPotts().getCellFieldG().getDim()
    MitosisClonesField=simthread.createFloatFieldPy(dim,"Mitosis_Clones")

if dye_flag:
    from ElongationModelSteppables import DyeCells
    dyeCells=DyeCells(_simulator=sim,_frequency=50,
        _x0 = params_container.getListParam('x0_dye'),
        _y0 = params_container.getListParam('y0_dye'),
        _xf = params_container.getListParam('xf_dye'),
        _yf = params_container.getListParam('yf_dye'),
        _reporter = reporter)
    dyeCells.setScalarField(Label01Field)
    steppableRegistry.registerSteppable(dyeCells) 
if dye_mitosis_clones:
    from ElongationModelSteppables import DyeMitosisClones
    dyeMitosisClones=DyeMitosisClones(_simulator=sim,_frequency=50,_window=mitosis_dye_window)
    dyeMitosisClones.setScalarField(MitosisClonesField)
    steppableRegistry.registerSteppable(dyeMitosisClones)

##  ****  Start the Simulation  *****  ##
CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
