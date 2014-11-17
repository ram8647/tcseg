from PlayerPython import * 
import CompuCellSetup
## General Note: Cell Address is relative to the anterior. So, a 0.0 address means that it is on the anterior tip.

from PySteppables import *
import CompuCell
import sys
import math

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

    def __init__(self,_simulator,_frequency, _y_target_offset, _pull_force_magnitude, _pinch_force_relative_center, _pinch_force_mag, _pinch_force_falloff_sharpness):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.y_target_offset = _y_target_offset
        self.pull_force_magnitude = _pull_force_magnitude
        self.pinch_force_relative_center = _pinch_force_relative_center
        self.pinch_force_mag = _pinch_force_mag
        self.pinch_force_falloff_sharpness = _pinch_force_falloff_sharpness
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
            for cell in self.cellList:
                self.stripe_y = 375
                if cell.yCOM < self.stripe_y+5 and cell.yCOM > self.stripe_y-5:
                    #cellDict["En_ON"] = True
                    cell.type = 2
                    if self.hinder_anterior_cells == True:
                        self.gene_product_secretor.secreteInsideCell(cell, 1)

    def step(self, mcs):
        if (mcs != 0) and (mcs % 300 == 0) :
            self.stripe_y -= 50
            SarrazinForces.setstripe_y(SarrazinForces, self.stripe_y)
            for cell in self.cellList:
                #cellDict = CompuCell.getPyAttrib(cell)
                print "self.stripe_y:    ", self.stripe_y
                if cell.type == 1: 
                    if cell.yCOM < self.stripe_y + 6 and cell.yCOM > self.stripe_y - 6:
                        #cellDict["En_ON"] = True
                        cell.type = 2
                        #if self.hinder_anterior_cells == True:
                            #self.gene_product_secretor.secreteInsideCell(cell,1)

        '''
        for cell in self.cellList:

            cellDict = CompuCell.getPyAttrib(cell)
            cell_address = cellDict["CELL_AP_ADDRESS"] # figure out where the cell is, accurate to within the last 100 mcs

            #reset cell variables here
            cellDict["En_ON"] = False
            cell.type = 1
            cell.lambdaSurface = 2.0

            ##******** Here, we assign which cells express EN ********##

            for stripe in self.stripes:
                if stripe.start_mcs < mcs:
                    spread = 0.0125    #  y - size of the stripe

                    #if cell_address < stripe.relative_position + spread and cell_address > stripe.relative_position - spread:
                    

            ##******** Here, we retard those cells within the domain of the EN gene product ********##

            #if self.hinder_anterior_cells == True:
                #cell.lambdaSurface = 2.0

                # ignore the EN expressing cells. It might be logical to remove this step later.
                #if cellDict["En_ON"] == False and self.gene_product_field[int(cell.xCOM), int(cell.yCOM), 0] > 4:
                #if self.gene_product_field[int(cell.xCOM), int(cell.yCOM), 0] > 0.1:
                    #cell.lambdaSurface = 60.0
'''

'''
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
'''