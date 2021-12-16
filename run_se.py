import os
import shutil
import subprocess
from datetime import datetime
import random


import argparse

def parse_trace(trace_file_path):
    full_trace_file_path = os.path.join(os.getcwd(), trace_file_path)
    assert(os.path.isdir(full_trace_file_path))
    filenames = os.listdir(full_trace_file_path)

    trace_path_list = []
    trace_name_list = []
    for filename in filenames:
        ext = os.path.splitext(filename)[-1]
        if ext == '.trace':
            full_filename = os.path.join(full_trace_file_path, filename)
            trace_path_list.append(full_filename)
            trace_name_list.append(os.path.splitext(filename)[0])

    return (trace_path_list, trace_name_list)

def make_simulation_dirs(trace_list):
    dirs_to_be_made = {}
    today = str(datetime.today().strftime('%Y_%m_%d'))
    # Simulation directory path. Simulation will run under this directory.
    # Note that under this directory, 
    # all simulations will use same binary and library files.
    # This occurs by copying binary and library files.
    sim_dir_path = \
        os.path.join(os.getcwd(), 
                  today)

    dirs_to_be_made['sim_dir_path'] = sim_dir_path

    for trace_info in trace_list:
        benchmark_name = trace_info
        trace_sim_dir_path = \
            os.path.join(sim_dir_path, benchmark_name)
        dirs_to_be_made[trace_info] = trace_sim_dir_path

    # Now, make directories.
    for _, dir_path in dirs_to_be_made.items():
        os.makedirs(dir_path, exist_ok = True)

    return dirs_to_be_made

def generate_sbatch_scripts(trace_name_list, trace_path_list, dirs_to_be_made):
    def get_slurm_node():
        #node_list = ['g5']
        node_list = ['n4', 'n1', 'n5', 'n6']
        #node_list = ['n4', 'n1', 'n6']
        #node_list = ['n4', 'n1', 'n5']
        #node_list = ['n4', 'n1']
        #node_list = ['n4', 'n1', 'n3']
        return node_list[random.randint(1, len(node_list)) - 1]
        #return 'n{}'.format(random.randint(2, 6))

    today = str(datetime.today().strftime('%Y_%m_%d'))
    for i, benchmark_name in enumerate(trace_name_list):
        trace_file_path = trace_path_list[i]
        app_sim_dir_path = dirs_to_be_made[benchmark_name]

        sbatch_content = ''
        env_content = ''
        run_content = ''

        sbatch_content += "#!/bin/bash\n\n"
        job_name = '{}/{}'.format(
            today, benchmark_name)
        sbatch_content += "#SBATCH --job-name={}\n".format(job_name)
        #sbatch_content += "#SBATCH --output=gpgpusim.result\n"
        sbatch_content += "#SBATCH --partition=allcpu\n"
        #sbatch_content += "#SBATCH --nodelist=g1\n"
        #sbatch_content += "#SBATCH --nodelist={}\n".format(get_slurm_node())
        #sbatch_content += "#SBATCH --exclude=g1\n"
        sbatch_content += "#SBATCH --parsable\n"
        sbatch_content += "\n"

        # Export LD_LIBRARY_PATH to make accelsim use the gpgpusim library file 
        # in the bin directory
        #env_content += "export LD_LIBRARY_PATH={}:$LD_LIBRARY_PATH\n".format(
        #    dirs_to_be_made['sim_lib_dir_path'])
        #env_content += "\n"

        run_content += \
            '/home/jmhhh/Documents/PIM/pim-simulator/ramulator /home/jmhhh/Documents/PIM/pim-simulator/configs/HBM-config.cfg --mode=dram' 
        run_content += " {} \\\n".format(trace_file_path)
        run_content += " > {}/output.txt".format(dirs_to_be_made[benchmark_name])
        run_content += "\n"

        with open(os.path.join(app_sim_dir_path, 'srun.sh'), 'w') as file:
            file.write(sbatch_content)
            file.write(env_content)
            file.write(run_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--trace',
                        type = str, 
                        help = "trace file path", 
                        dest = "trace_file_path",
                        default = "Newton_trace")
    args = parser.parse_args()
    
    trace_path_list, trace_name_list = parse_trace(args.trace_file_path)

    dirs = make_simulation_dirs(trace_name_list)

    generate_sbatch_scripts(trace_name_list, trace_path_list, dirs)

    app_sim_dir_paths = []
    for benchmark_name in trace_name_list:
        key = benchmark_name
        if key in dirs:
            app_sim_dir_paths.append(dirs[key])
            print(dirs[key])
    
    num_launched = 0
    for app_sim_dir_path in app_sim_dir_paths:
        # Change current directory to run sbatch command.
        os.chdir(app_sim_dir_path)
        # Run sbatch command.
        jobid = subprocess.check_output(
            ['sbatch', '--export=ALL', 'srun.sh'], encoding = 'utf-8')
        jobid = jobid.strip()
        # Accumulate the number of simulation launched.
        num_launched += 1

    print("You launched {} simulation(s)".format(num_launched))