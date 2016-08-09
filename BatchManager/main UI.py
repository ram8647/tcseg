import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from collections import OrderedDict
from BatchManagerScripts import ModelIOManager
from BatchManagerScripts import ResetBatch
from BatchManagerScripts import StepBackBatch
from BatchManagerScripts import ParamsPackager
from BatchManagerScripts import Convert2Video
from BatchManagerScripts import CompressVTKs
from BatchManagerScripts import InvokeCompuCell
from BatchManagerScripts import CreateSummary

# List the things that Manager can do.
options_dict = OrderedDict()
options_dict['Run batch'] = 'run_batch'
options_dict['Delete all simulation output'] = 'reset'
options_dict['Delete/redo the most recent simulation'] = 'step_back'
options_dict['Input file locations'] = 'input_file_paths'
options_dict['Update file locations in ElongationModel.py'] = 'sync'
options_dict['Convert a params.txt to .xml format'] = 'convert_any_txt_file2xml'
options_dict['Process output (i.e. move files, create summary and create videos)'] = 'process_all'

def convert_txt2xml(inpath):
    if inpath.endswith('.xml'):
        print 'The current params file is already an XML file'
    elif inpath.endswith('.txt'):
        dict = ParamsPackager.load_params_dict(inpath)
        xml_str = ParamsPackager.create_xml_from_params_dict(dict)
        ParamsPackager.write_xml_to_sim_directory(xml_str)
        user_input = raw_input('Do you want to use this xml file from now on? (Type \'yes\' to do so)')
        if user_input.lower() == 'yes':
            io_manager.params_path = io_manager.params_path.replace('.txt','.xml')
            io_manager.write_settings_XML_file()
    else:
        print 'The current params file is of unknown type. (File path = {}.) Aborting.'.format(inpath)

def process_all():
    convert2vid()
    compress_vtks()
    io_manager.move_all_files_to_output_folder()
    io_manager.delete_unnecessary_files()
    create_summary()

def convert_any_txt_file2xml():
    path2xml = raw_input('Please input the location of the params.txt')
    convert_txt2xml(path2xml)

def run_batch():
    sync()
    InvokeCompuCell.invoke_compucell()

def reset_and_run_batch():
    reset()
    run_batch()

def input_file_paths():
    io_manager.user_input_io_xml()

def sync():
    io_manager.update_file_path_in_elongation_model_python()

def reset():
    ResetBatch.reset()

def step_back():
    StepBackBatch.step_back()

def convert2vid():
    Convert2Video.convert_pngs_to_vid()

def compress_vtks():
    CompressVTKs.compressVTKs()

def update_parameter_scan_specs():
    ParamsPackager.update()

def create_summary():
    CreateSummary.create_summary()


def window():
    app = QApplication(sys.argv)
    w = QWidget()

    b0 = QPushButton('Update Simulation Files')
    b0.clicked.connect(sync)
    b1 = QPushButton('Delete all output')
    b1.clicked.connect(reset)
    b2 = QPushButton('Delete output from last run')
    b2.clicked.connect(step_back)
    b3 = QPushButton('Create summary')
    b3.clicked.connect(create_summary)
    b4 = QPushButton('Create videos')
    b4.clicked.connect(convert2vid)
    b5 = QPushButton('Compress VTKs')
    b5.clicked.connect(compress_vtks)
    b6 = QPushButton('Process ALL Output')
    b6.clicked.connect(process_all)

    buttons = [b0, b1, b2, b3, b4, b5, b6]

    vbox = QVBoxLayout()

    for push_button in buttons:
        vbox.addWidget(push_button)
        vbox.addStretch()

    w.setLayout(vbox)
    w.setGeometry(10,10,300,50)
    w.setWindowTitle('Batch Manager')
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    io_manager = ModelIOManager.IOManager(_silent=False)
    window()
