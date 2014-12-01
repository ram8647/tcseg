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
  1. $ git fetch upstream
  2. $ git checkout master
  3. $ git merge upstream/master

Standard work flow in Terminal Window
=====================================
1. Sync with upstream repo
  1. $ git fetch upstream
  2. $ git checkout master
  3. $ git merge upstream/master
2. From the master branch create a new work branch and switch to that branch
  1. $ git branch taskname
  2. $ git checkout taskname
3. Make edits to the files you're going to change, e.g.,  file/test code/etc
4. $ git add --all                     # Add all the changed files to the changeset
5. $ git commit -m "taskname message"  # Commit the changeset, giving it a short message
6. $ git checkout master               # Switch back to the master branch
7. Sync with upstream again            # Same as step 1 (in case others have changed the repo)
8. $ git merge taskname                # Merge the changeset from the taskname branch
9. $ git push                          # Push the changes (this pushes to your clone of the main repo)
10. $ git push upstream                # Push the changes to the main repo (assuming you are a collaborator)
11. $ git branch -d taskname           # Optional: Delete your task branch once you're sure your changes are in the repo


To Run the Model
================
 1. Run Compucell3D (CC3D_3.7.1) by double clicking on CC3D_3.7.1/compucell3d.command
 2. This will open a console and the GUI player
 3. To open a model: File > Open Simulation File (.cc3d)
 4. To run it, click on the player's run icon
 5. Debugging runtime comments appear in the console.

hello from Peter
hello from Effie
here is Terri's test

