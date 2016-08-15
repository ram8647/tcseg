import os, os.path, subprocess
import platform
from ModelIOManager import IOManager

def invoke_compucell(io_manager):
    '''
    calls CompuCell with user-provided command and uses the correct arguments automatically
    :type io_manager: IOManger
    '''
    if platform.system() == 'Darwin':
        invoke_compucell_mac(io_manager)
    else:
        invoke_compucell_other_platforms(io_manager)

def invoke_compucell_other_platforms(io_manager):
    cmd = '{} &'.format(io_manager.cc3d_command_dir)
    os.system(cmd)

def invoke_compucell_mac(io_manager):
    '''
    not supported yet, yet this function will restart CompuCell if it crashes before the completion of
    the batch runs. It handles crashes in a way that only works on mac.
    '''
    def batch_completed():
        required_dir = os.path.join(io_manager.screenshot_output_path, str(io_manager.number_of_runs() - 1))
        return os.path.isdir(required_dir)

    while not batch_completed():
        cmd = 'osascript {} & {}'.format(io_manager.apple_script_dir.replace(' ','\ '), io_manager.cc3d_command_dir)
        shell_output = subprocess.check_output(cmd, shell=True)
        print(shell_output)