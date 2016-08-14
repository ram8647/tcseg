import shutil
import os, os.path
from ModelIOManager import IOManager

def compressVTKs(io_manager):
    '''
    compress VTK archives the VTK and screenshot description file in the ParameterScan folder,
    which considerably decreases their file size
    :type io_manager: IOManger
    '''
    for root, dirs, files in os.walk(io_manager.screenshot_output_path):
        for name in dirs:
            if name == 'LatticeData':
                archive_path = os.path.join(root, name)
                parent_path = os.path.dirname(os.path.normpath(archive_path))
                batch_iteration = os.path.basename(parent_path)

                shutil.make_archive(archive_path, 'zip', archive_path)

                zip_name = 'batch_run_{}_vtk_files.zip'.format(batch_iteration)
                new_path = os.path.join(parent_path, zip_name)
                old_path = os.path.join(parent_path, 'LatticeData.zip')

                os.rename(old_path, new_path)