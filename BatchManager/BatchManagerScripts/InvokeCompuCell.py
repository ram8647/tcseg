import os, os.path, subprocess
from ModelIOManager import IOManager

def invoke_compucell(io_manager):
    '''
    calls CompuCell with user-provided command and uses the correct arguments automatically
    :type io_manager: IOManger
    '''

    #Make sure the string is properly formatted
    inpath = io_manager.model_cc3d_file
    inpath = inpath.replace(' ', '\ ')
    inpath = inpath.replace('\ ', ' ')

    cmd = '{} &'.format(inpath)
    os.system(cmd)

def invoke_compucell_repeatedly(manager):
    '''
    not supported yet, yet this function will restart CompuCell if it crashes before the completion of
    the batch runs
    '''
    def batch_completed():
        required_dir = os.path.join(manager.screenshot_output_path, str(manager.number_of_runs() - 1))
        return os.path.isdir(required_dir)

    inpath = manager.model_cc3d_file.replace(' ','\ ')
    max_runs = manager.number_of_runs()

    while not batch_completed():
        cmd = '{} --exitWhenDone'.format(manager.cc3d_command_dir)
        try:
            #shell_output = subprocess.check_output(cmd, shell=True)
            print(shell_output)
        except:
            raise NameError('Error!')