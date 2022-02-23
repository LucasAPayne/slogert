"""
Contains functions for calling and working with SLOGERT to generate knowledge graphs and combine them
"""

import os
import shutil
import time
import yaml
from pathlib import Path

"""
The main function for generating knowledge graphs that calls SLOGERT on the specified files
args: command line arguments defined in slogert.py
"""
def gen_kg(args):
    start = time.time()
    config_path = Path("src/test/resources/")
    in_path = Path("input/")

    # The name of the .ttl file used as output for generating a KG is the name given in the argument, or output.ttl if no name is given
    # The file name is the text left over after the last '/'
    ttl_name = args.outfile.split('/')[-1] if args.outfile else "output.ttl" 

    # Create folder for output named for ttl file (e.g., data/train.ttl creates folder data/train)
    # The directory path is the outpath until the last '/'
    out_path = Path(args.outfile[:args.outfile.rfind('/')]) 

    # Create output directory if it does not exist
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    slogert_version = get_slogert_version()

    files = get_files(in_path, config_path, args)

    # Call SLOGERT on all config files that have associated input logs
    for f in files:
        os.system("java -jar target/{0} -c src/test/resources/{1}".format(slogert_version, f))

    combine_KGs(out_path, ttl_name)

    if not args.save_temps:
        shutil.rmtree(Path("output/"))

    # Move output file to output directory
    if os.path.exists(ttl_name):
        shutil.move(ttl_name, os.path.join(out_path, ttl_name))

    print("****** End of KG aggregation")
    end = time.time()
    print("*** KG generated in {:.2f}s".format(end - start))


"""
Returns the SLOGERT .jar file with dependencies to be used when SLOGERT is called
"""
def get_slogert_version():
    version = [f for f in os.listdir("target/") if f.endswith("with-dependencies.jar")]
    return version[0]


"""
Determines if there is a log file in the input folder that matches the source type of the given config file
config_file: SLOGERT config file corresponding to a log type
input_files: the files located in the in_path, where log files to be processed are located
"""
def source_match(config_file, input_files):
    # Keep only the config files that have relevant input log files
    # e.g., if there is no auth.log, SLOGERT will not be called with auth-config.yaml
    with open(config_file, "r") as file:
        config_data = yaml.safe_load(file)
        
        for input_file in input_files:
            if input_file.name == config_data["source"]:
                return True
        
        return False


"""
Gets all files that SLOGERT will be called on
Returns all relevant config files if --all flag is set, otherwise returns files specified with --files argument
in_path: path to log files to be processed
config_path: path to SLOGERT config files corresponding to log types
args: command line arguments defined in the main function
"""
def get_files(in_path, config_path, args):
    # Get all config and input files
    config_files = [f for f in config_path.glob("**/*") if f.is_file() and f.name.endswith(".yaml")]
    input_files = [f for f in in_path.glob("**/*") if f.is_file()]

    sources = []
    if args.all:
        for f in config_files:
            if source_match(f, input_files):
                sources.append(f.name)
    elif args.files is not None:
        for f in args.files:
            file = Path(config_path / f)
            if source_match(file, input_files):
                sources.append(f)

    return sources


"""
Get output files after SLOGERT has run, and combine all separate KGs into one
out_path: path to where the output of this script will be written
ttl_name: the name of the .ttl knowledge graph file to be created
"""
def combine_KGs(out_path, ttl_name):
    # Note that SLOGERT puts intermediate files in the output directory, not the out_path created in this script
    output_files = [f for f in Path("output/").glob('**/*') if f.is_file() and f.name.endswith(".ttl") and not f.name.endswith("template.ttl") and not f.name == ttl_name]
    with open(os.path.join(out_path, ttl_name), "w", encoding="utf-8") as outfile:
        print("*** Combining .ttl files...")
        start = time.time()
        
        # Loop through .ttl files, exlcuding .ttl.log files
        for count, f in enumerate(output_files):
            with open(f, "r", encoding="utf-8") as infile:
                # Loop through each line of the file and copy it to the output file
                # If the file is not the first encountered, delete the prefixes, as they should be constant between all files
                for line in infile:
                    if count == 0 or (count > 0 and not line.startswith("@prefix")):
                        outfile.write(line)
        
        end = time.time()
        print("*** Combined .ttl files in {:.2f}s".format(end - start))
