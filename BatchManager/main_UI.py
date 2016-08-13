#!/usr/bin/env python

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from collections import OrderedDict
from BatchManagerScripts import ModelIOManager
from BatchManagerScripts import ResetBatch
from BatchManagerScripts import StepBackBatch
from BatchManagerScripts import ParamsPackager
from BatchManagerScripts import Convert2Video
from BatchManagerScripts import CompressVTKs
from BatchManagerScripts import CreateSummary

# Set up the gui
def window(io_manager):
    '''
    Set up the functions that the GUI calls, then use PyQt to set up the GUI
    '''

    # Manage Input
    def new_params_path():
        params_path = QFileDialog.getOpenFileName(w, 'Cannot find params file. Please Open Params.xml...', '/')
        params_path = unicode(params_path)
        if params_path != '': # This will be the case if the user cancels the operation
            io_manager.params_path = params_path
            io_manager.write_settings_XML_file()
            update_file_paths_in_elongation_model_py()

    def update_file_paths_in_elongation_model_py():
        io_manager.update_file_path_in_elongation_model_python()

    # Delete old output
    def delete_all_output():
        ResetBatch.reset(io_manager)

    def delete_last_runs_output():
        StepBackBatch.step_back(io_manager)

    # Manage Output
    def convert2vid():
        Convert2Video.convert_pngs_to_vid(io_manager)

    def compress_vtks():
        CompressVTKs.compressVTKs(io_manager)

    def create_summary():
        CreateSummary.create_summary(io_manager)

    def move_output2output_folder():
        io_manager.move_all_files_to_output_folder()

    def process_all():
        convert2vid(io_manager)
        compress_vtks(io_manager)
        io_manager.move_all_files_to_output_folder()
        io_manager.delete_unnecessary_output_files()
        create_summary(io_manager)

    # Not supported yet
    def convert_txt2xml(inpath):
        if inpath.endswith('.xml'):
            print 'The current params file is already an XML file'
        elif inpath.endswith('.txt'):
            dict = ParamsPackager.load_params_dict(inpath)
            xml_str = ParamsPackager.create_xml_from_params_dict(dict)
            ParamsPackager.write_xml_to_sim_directory(xml_str, io_manager)
            user_input = raw_input('Do you want to use this xml file from now on? (Type \'yes\' to do so)')
            if user_input.lower() == 'yes':
                io_manager.params_path = io_manager.params_path.replace('.txt', '.xml')
                io_manager.write_settings_XML_file()
        else:
            print 'The current params file is of unknown type. (File path = {}.) Aborting.'.format(inpath)

    # Build the GUI
    app = QApplication(sys.argv)
    w = QWidget()

    b0 = QPushButton('Open new params file')
    b0.clicked.connect(new_params_path)
    b1 = QPushButton('Update files paths in ElongationModel.py')
    b1.clicked.connect(update_file_paths_in_elongation_model_py)
    b2 = QPushButton('Delete all output')
    b2.clicked.connect(delete_all_output)
    b3 = QPushButton('Delete output from last run')
    b3.clicked.connect(delete_last_runs_output)
    b4 = QPushButton('Create summary')
    b4.clicked.connect(create_summary)
    b5 = QPushButton('Create videos')
    b5.clicked.connect(convert2vid)
    b6 = QPushButton('Compress VTKs')
    b6.clicked.connect(compress_vtks)
    b7 = QPushButton('Move output to output folder')
    b7.clicked.connect(move_output2output_folder)
    b8 = QPushButton('Do all four')
    b8.clicked.connect(process_all)

    l1 = QLabel('Manage Input')
    l2 = QLabel('Delete Old Output')
    l3 = QLabel('Manage Output')

    widgets = [l1, b0, b1, l2, b2, b3, l3, b4, b5, b6, b7, b8]

    vbox = QVBoxLayout()
    for widget in widgets:
        vbox.addWidget(widget)

    w.setLayout(vbox)
    w.setGeometry(10,10,300,50)
    w.setWindowTitle('Batch Manager')
    w.show()

    for msg in io_manager.GUI_messages:
        print 'Dealing with message: \'{}\''.format(msg)
        if msg == 'ask_for_params':
            msg_box = QMessageBox()
            msg_box.setText('Please Open Params.xml')
            msg_box.exec_()
            params_path = QFileDialog.getOpenFileName(w, 'Cannot find params file. Please Open Params.xml...', '/')
            params_path = unicode(params_path)
            io_manager.params_path = params_path
        elif msg == 'ask_for_compucell_command':
            msg_box = QMessageBox()
            msg_box.setText('Please Open CompuCell.command')
            msg_box.exec_()
            cc3d_command_dir = QFileDialog.getOpenFileName(w, 'Cannot find CompuCell.command Please Open CompuCell.command', '/')
            cc3d_command_dir = unicode(cc3d_command_dir)
            io_manager.cc3d_command_dir = cc3d_command_dir
        elif msg == 'ask_for_output_folder':
            msg_box = QMessageBox()
            msg_box.setText('Please open the folder where output will be kept')
            msg_box.exec_()
            output_folder_dir = QFileDialog.getOpenFileName(w, 'Cannot find output folder. Please Open Output Folder', '/')
            output_folder_dir = unicode(cc3d_command_dir)
            io_manager.output_folder = output_folder_dir
        elif msg == 'ask_for_model_folder':
            msg_box = QMessageBox()
            msg_box.setText('Please Open tcseg_batch.cc3d')
            msg_box.exec_()
            tcseg_cc3d_dir = QFileDialog.getOpenFileName(w,'Cannot find tcseg_batch.cc3d Please Open tcseg_batch.cc3d','/')
            tcseg_cc3d_dir = unicode(cc3d_command_dir)
            model_dir = os.path.abspath(os.path.join(tcseg_cc3d_dir, os.pardir))
            io_manager.model_path = model_dir
        else:
            raise NameError('Unknown error from IOManager: {}'.format(msg))

        io_manager.construct_additional_paths()
        io_manager.write_settings_XML_file()

    sys.exit(app.exec_())

if __name__ == '__main__':
    io_manager = ModelIOManager.IOManager(_silent=False)
    window(io_manager)
