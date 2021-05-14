# general imports
import argparse
import sys
import os
import csv
from copy import deepcopy
import subprocess
import sys
from pathlib import Path
import time

# name batch generator
def script_generation(batch_file, machine, base_dir, run_directory):

    # get all yaml files in a directory
    yaml_files = []
    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith(".yaml"):
                yaml_files.append(filename)
            else:
                continue

    # create the primary batch file
    file = open(batch_file, "w")
    file.write("# Wandb Generated Output \n")

    # add commands to batch
    prefix = 'wandb sweep '
    suffix = ' > temp.txt 2>&1'

    # iterate through all files and add each
    for yaml_gen in yaml_files:

        # compute wandb command
        command = prefix + yaml_gen + suffix
        exit_status = subprocess.call(command, shell=True)
        temp_text = open('temp.txt')
        wandb_command_line=temp_text.readlines()[-1]
        wandb_command = wandb_command_line.split("wandb: Run sweep agent with: ")[-1][:-1]

        # create sweep generator command
        sweep_command = 'python sweep_runner.py --machine ' + machine + ' '
        sweep_command = sweep_command + '--command "' + wandb_command + '" '
        sweep_command = sweep_command + '--directory ' + run_directory + ' '
        sweep_command = sweep_command + '--job_name ' + '1'

        # write command to batch script
        file.write(sweep_command + "\n")

        # clean-up
        temp_text.close()
        os.remove('temp.txt')

    # clean-up
    file.close()

#
def main():
    # pick up args
    parser = argparse.ArgumentParser(description='job runner')
    parser.add_argument('--base_dir', default='./sweeps/bc/random_sweeps')
    parser.add_argument('--batch_file', default='batch_script.sh')
    parser.add_argument('--machine', default='borg')
    parser.add_argument('--run_directory', default='/ubc/cs/research/plai-scratch/wlaving/opo_sls/compact_state')
    parser.add_argument('--generate_exp_dir', default='./sweeps/bc/generate_exp_dir.py')
    args = parser.parse_args()
    # generate experiment yaml files
    exit_status = subprocess.call('python '+args.generate_exp_dir, shell=True)
    # create wandb sweeps
    script_generation(batch_file=args.batch_file, base_dir=args.base_dir, \
        run_directory=args.run_directory, machine=args.machine)

#
if __name__ == "__main__":
    main()
