tcseg
=====

Source code for the Tribolium casteneum (Tc) segmentation modeling project on the CompuCell platform.

This project manages the Python source code for a CompuCell modeling project. CompuCell3D is an open-source simulation environment for multi-cell, single-cell-based modeling of tissues, organs and organisms.  It uses Cellular Potts Model to model cell behavior.  This CompuCell project is funded by the NIH and EPA.  Compucell3D is led by Maciej Swat (IU), James Glazier(IU) and Roshan D'Souza (U.Wisc. Milwaukee)

The Tribolium c. modeling project is funded by a grant from the National Science Foundation. It is led by Terri Williams and Ralph Morelli (Trinity College) and Susan Hester (Unversity of Arizona).  Student research assistants include:

   * Yuxuan (Effie) Li, Trinity 2017
   * Peter Jong, Trinity 2017

The focus of the project is to create a Monte-Carlo cellular-level model of the process of segmentation in an arthropod. 

There are three main source files that make up the Simulation.  These are typically found in the /Simulation folder of a ComputCell project.
 
 *  <projectname>.py -- initialization file
 *  <projectname>Steppables.py -- scripts that define the steps that are performed on each Monte Carlo step.
 *  <name>.piff  -- initial layout of cell lattice
 *  
 
