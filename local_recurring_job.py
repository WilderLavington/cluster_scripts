# general imports
import argparse
import sys
import os
from copy import deepcopy
import subprocess
from pathlib import Path
import time
import uuid

def eval_generation(job_name='1', machine='borg', command='', directory='.',
                    run_time='00-24:00', gpus='4', cpu_gpu='5', cpu_task='8',
                    single_node=True, mem='10G', write_out='out.txt'):
    # make thhe directory if it does not exist
    Path('eval_dir').mkdir(parents=True, exist_ok=True)
    # set the base runner
    args_list = sys.argv[1:]
    if machine=='borg':
        file = open('eval_dir/job_'+job_name+'.sh',"w+")
        file.write('#!/bin/sh \n')
        file.write('#SBATCH --partition=plai \n')
        file.write('#SBATCH --gres=gpu:'+gpus+' \n')
        file.write('#SBATCH --cpus-per-gpu='+cpu_gpu+' \n')
        if single_node:
            file.write('#SBATCH --nodes=1 \n')
        file.write('#SBATCH --time='+run_time+'     # time (DD-HH:MM) \n')
        file.write('cd ' + directory + ' \n')
        file.write(command + ' \n')
        file.write('exit')
        file.close()
    else:
        file = open('eval_dir/job_'+job_name+'.sh',"w+")
        file.write('#!/bin/sh \n')
        file.write('#SBATCH --account=def-fwood \n')
        file.write('#SBATCH --mem='+mem+' \n')
        file.write('#SBATCH --cpus-per-task='+cpu_task+' \n')
        file.write('#SBATCH --time='+run_time+'     # time (DD-HH:MM) \n')
        file.write('#SBATCH --gres=gpu:p100:'+gpus+' \n')
        file.write('cd ' + directory + ' \n')
        file.write('export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \n')
        file.write(command + ' \n')
        file.write('exit')
        file.close()
    # create the command
    command = 'sbatch ' + 'eval_dir/job_'+job_name+'.sh'+' > '+write_out
    # # submit the job
    exit_status = subprocess.call(command, shell=True)
    exit_status = subprocess.call('echo "\nsubmitted:"', shell=True)
    command = 'cat eval_dir/job_'+job_name+'.sh'
    exit_status = subprocess.call(command, shell=True)
    exit_status = subprocess.call('echo "\n"', shell=True)
    # now delete the file
    os.remove('eval_dir/job_'+job_name+'.sh')
    # nothing to return
    return write_out


def read_outfile(file_name):
    # grab first line
    with open(file_name) as f:
        first_line = f.readline()
    # split it up
    split_line = first_line.split()
    # return second to last id
    return split_line[-1]

def get_joblist(file_name='recur_temp.txt'):
    # write info
    command = 'squeue -u $USER' + ' > ' + file_name
    exit_status = subprocess.call(command, shell=True)
    #
    jobs = []
    # grab llist of active jobs
    with open(file_name) as fp:
        for i, line in enumerate(fp):
            print(line)
            if i > 0:
                job_id = line.split()[0]
                jobs.append(job_id)
    # remove old file
    os.remove(file_name)
    # return second to last id
    return jobs

def recurring_job(job_name='1', machine='borg', command='', directory='.',
                    run_time='00-23:00', gpus='4', cpu_gpu='5', cpu_task='8',
                    single_node=True, mem='10G', interval=24):

    #
    start_time = time.time()
    restart_time = interval * 3600
    max_exec = 21
    current_exec = 1
    #
    unique_out_file=str(uuid.uuid4())+'.txt'

    # run job
    write_out = eval_generation(job_name=job_name, machine=machine, command=command, directory=directory,
                            run_time=run_time, gpus=gpus, cpu_gpu=cpu_gpu, cpu_task=cpu_task,
                            single_node=single_node, mem=mem, write_out=unique_out_file)

    # read the job_id
    current_job_id = read_outfile(unique_out_file)

    #
    while True:

        #
        current_time = time.time()
        elapsed_time = current_time - start_time

        #
        if elapsed_time > restart_time:

            # update start-tim
            start_time = time.time()

            # check current are still queued
            recurring_job_id = get_joblist(unique_out_file)
            if current_job_id in recurring_job_id:
                # print messages
                print("job " + current_job_id  + " still in proccess, restarting countdown.")
                # sleep for an hour
                time.sleep(restart_time)
                pass
            # pushing the job again
            else:
                eval_generation(job_name=job_name, machine=machine, command=command, directory=directory,
                                    run_time=run_time, gpus=gpus, cpu_gpu=cpu_gpu, cpu_task=cpu_task,
                                    single_node=single_node, mem=mem, write_out=unique_out_file)
                current_job_id = read_outfile(unique_out_file)
                current_exec += 1
                print("new job submitted: "+current_job_id)

        #
        if current_exec >= max_exec:
            print("Finished iterating in: " + str(int(elapsed_time))  + " seconds")
            os.remove(unique_out_file)
            break

    # nothing to return
    return None

def main():
    parser = argparse.ArgumentParser(description='job runner')
    # general shit
    parser.add_argument('--directory', default='/ubc/cs/research/plai-scratch/wlaving/inverted_rl')
    parser.add_argument('--command', default='echo "hello-world"')
    parser.add_argument('--machine', default='borg')
    parser.add_argument('--job_name', default='recurring-submission')
    # submission info
    parser.add_argument('--interval', default=0.5)  # time (DD-HH:MM)
    parser.add_argument('--run_time', default='00-24:00')
    parser.add_argument('--gpus', default='4')
    parser.add_argument('--cpu_gpu', default='5')
    parser.add_argument('--cpu_task', default='8')
    parser.add_argument('--single_node', default=1)
    parser.add_argument('--mem', default='10G')
    args = parser.parse_args()
    recurring_job(machine=args.machine, command=args.command,
                  directory=args.directory, job_name=args.job_name,
                  run_time=args.run_time, gpus=args.gpus, cpu_gpu=args.cpu_gpu,
                  cpu_task=args.cpu_task, single_node=args.single_node,
                  mem=args.mem, interval=args.interval)

if __name__ == "__main__":
    main()
