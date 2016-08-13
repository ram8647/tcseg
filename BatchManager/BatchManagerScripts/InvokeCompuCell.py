import os, os.path, subprocess
from ModelIOManager import IOManager

def invoke_compucell(manager):
    inpath = manager.model_cc3d_file.replace('\ ', ' ')
    inpath = inpath.replace(' ', '\ ')

    cmd = '{} &'.format(manager.cc3d_command_dir)
    os.system(cmd)

def invoke_compucell_repeatedly(manager):

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

#invoke_compucell(IOManager())