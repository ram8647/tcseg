tcseg
=====

Source code for the Tribolium casteneum (Tc) segmentation modeling project on the CompuCell platform.

This project manages the Python source code for a CompuCell modeling project. CompuCell3D is an open-source simulation environment for multi-cell, single-cell-based modeling of tissues, organs and organisms.  It uses Cellular Potts Model to model cell behavior.  This CompuCell project is funded by the NIH and EPA.  Compucell3D is led by Maciej Swat (IU), James Glazier(IU) and Roshan D'Souza (U.Wisc. Milwaukee)

The Tribolium c. modeling project is funded by a grant from the National Science Foundation. It is led by Terri Williams and Ralph Morelli (Trinity College) and Susan Hester (Unversity of Arizona).  Student research assistants include:

* Yuxuan (Effie) Li, Trinity 2017
* Peter Jung, Trinity 2017

The focus of the project is to create a Monte-Carlo cellular-level model of the process of segmentation in an arthropod. 

There are three main source files that make up the Simulation.  These are typically found in the /Simulation folder of a ComputCell project.
These are the files that will typically be edited and revised during development.
 
 *  Simulation/RewrittenSarrazin.py -- initialization file
 *  Simulation/RewrittenSarrazinSteppables.py -- scripts that define the steps that are performed on each Monte Carlo step.
 *  Simulation/new.piff  -- initial layout of cell lattice

There is also the main simulation (.cc3d) file.  This does not need editing:

 * RewrittenSarrazin.cc3d
 
To sync with upstream ram8647/tcseg
====================================
 $ git fetch upstream
 $ git checkout master
 $ git merge upstream/master

Standard work flow
=================
1. Sync with upstream repo
2. From master $ git branch taskname
3. Edit file/test code/etc
4. $ git add --all
5. $ git commit -m "tastname message"
6. $ git checkout master
7. Sync with upstream again
8. $ git merge taskname
9. $ git push
10.$ git push upstream
11.$ git granch -d taskname 


To Run the Model
================
 1. Run Compucell3D (CC3D_3.7.1) by double clicking on CC3D_3.7.1/compucell3d.command
 2. This will open a console and the GUI player
 3. To open a model: File > Open Simulation File (.cc3d)
 4. To run it, click on the player's run icon
 5. Debugging runtime comments appear in the console.

Testing Ralph 
Hello Terri
