import os, os.path, subprocess
from ModelIOManager import IOManager


def invoke_compucell():
    manager = IOManager()

    def batch_completed():
        required_dir = os.path.join(manager.screenshot_output_path, str(manager.number_of_runs() - 1))
        return os.path.isdir(required_dir)

    # def did_last_run_crash():
    #     return False

    inpath = manager.model_cc3d_file.replace(' ','\ ')
    max_runs = manager.number_of_runs()

    while not batch_completed():
        cmd = '{} --exitWhenDone'.format(manager.cc3d_command_dir)
        try:
            shell_output = subprocess.check_output(cmd, shell=True)
            print(shell_output)
        except:
            raise NameError('Error!')