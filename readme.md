##BEFORE USING THE MODEL

On a Mac, open 'Batch Manager.command'. On a Windows computer, open a command prompt, cd to the 'BatchManager' directory and run 'python ./main.py'

This will open the Batch Manager. Choose 'Input File Locations' and follow the prompts. This will set up the file system.

NOTE: Unfortunetly, due to an error in CompuCell, filepaths must be hard-coded when running simulations in batches. Therefore, if you change the location of any of asked-about files, you must  redo 'Input File Locations' as described above.

Now, you may run the simulation like normal 

##WHEN USING THE MODEL

There are two options for using the model. You can run 'tcseg.cc3d,' which runs the simulation once; alternately, you can use 'tcseg_batch_.cc3d' to run the simulation multiple times. However, in the latter case, make sure to use a proper params.xml!

Contact Jeremy about how to write a params.xml for running the simulation in batches.