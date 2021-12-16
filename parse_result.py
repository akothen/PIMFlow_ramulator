import os
import shutil
import subprocess
from datetime import datetime
import random
import argparse
import pandas as pd

def parse_trace(trace_file_path):
    full_trace_file_path = os.path.join(os.getcwd(), trace_file_path)
    assert(os.path.isdir(full_trace_file_path))
    filenames = os.listdir(full_trace_file_path)

    trace_path_list = []
    trace_name_list = []
    for filename in filenames:
        full_file_path = os.path.join(full_trace_file_path, filename, 'output.txt')
        trace_path_list.append(full_file_path)
        trace_name_list.append(filename)

    return (trace_path_list, trace_name_list)

def parse_output(target_path):
    assert(os.path.isfile(target_path))
    energy_list = ['COMP', 'GWRITE', 'READRES', 'PRE', 'Total']
    energy = {'COMP' : 0.0, 'GWRITE': 0.0, 'READRES' : 0.0, 'PRE' : 0.0, 'Total' : 0.0} #COMP energy 9.87266e-06
    cycle = 0
    with open(target_path, 'r') as output:
        for line in output:
            if 'energy' in line:
                start_word = line.split()[0]
                for energy_target in energy_list:
                    if energy_target == start_word:
                        energy[energy_target] = float((line.split())[2])
            if 'Cycle' in line:
                cycle = int((line.split())[1])
    return cycle, energy
            
def parse_all_output(trace_path_list, trace_name_list):
    result = {} #kernel : (cycle, {'COMP' : 0.0, 'GWRITE': 0.0, 'READRES' : 0.0, 'PRE' : 0.0, 'Total' : 0.0})

    for i, trace_name in enumerate(trace_name_list):
        cycle, energy = parse_output(trace_path_list[i])
        result[trace_name] = {'Cycle' : cycle, 'Energy' : energy}
    return result
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--output',
                        type = str, 
                        help = "trace file path", 
                        dest = "trace_file_path",
                        default = "2021_12_16")
    args = parser.parse_args()

    trace_path_list, trace_name_list = parse_trace(args.trace_file_path)

    result = parse_all_output(trace_path_list, trace_name_list)

    df = pd.DataFrame.from_dict(result, orient='index') # convert dict to dataframe

    df.to_csv('result.csv') # write dataframe to file