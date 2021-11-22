"""
Combine the separate .ttl files generated by SLOGERT into one .ttl file
"""

import argparse
import os
import shutil
import time
import yaml
from pathlib import Path

def main():
    # Define CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--intermediate", "-i", help="keeps all intermediate files", action="store_true")
    parser.add_argument("--all", "-a", help="run SLOGERT on all config files", action="store_true")
    parser.add_argument("--files", "-f", nargs="+", help="names of config files to run SLOGERT on")
    parser.add_argument("--update", "-u", help="rebuild SLOGERT with Maven to capture changes to config files", action="store_true")
    args = parser.parse_args()

    # If updating SLOGERT, only update, then return
    # Rebuild with Maven, and skip tests, used mainly for capturing changes to config files
    if args.update:
        os.system("mvn install -DskipTests")
        return

    # Define paths to input, output, and config files
    in_path = Path("input/")
    out_path = Path("output/")
    config_path = Path("src/test/resources")

    files = get_files(in_path, config_path, args)
    print(files)

    # Call SLOGERT on all config files that have associated input logs
    # NOTE: Might be useful to get SLOGERT version and have that as another parameter for future-proofing
    for f in files:
        os.system("java -jar target/slogert-1.0.0-SNAPSHOT-jar-with-dependencies.jar -c src/test/resources/{0}".format(f))

    combine_KGs(out_path)

    if not args.all:
        remove_intermediates(out_path)

    # Move output file to output directory
    if Path("output.ttl").is_file():
        shutil.move("output.ttl", out_path)

    print("****** End of KG aggregation")


"""
Determines if there is a log file in the input folder that matches the source type of the given config file
"""
def source_match(file, input_files):
    # Keep only the config files that have relevant input log files
    # e.g., if there is no auth.log, SLOGERT will not be called with auth-config.yaml
    with open(file, "r") as file:
        config_data = yaml.safe_load(file)
        
        for input_file in input_files:
            if input_file.name == config_data["source"]:
                return True
        
        return False


"""
Gets all files that SLOGERT will be called on
Returns all relevant config files if --all flag is set, otherwise returns files specified with --files argument
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

    print("No files specified! Use -h argument for help.")
    return sources


"""
Get output files after SLOGERT has run, and combine all separate KGs into one
"""
def combine_KGs(out_path):
    output_files= [f for f in out_path.glob('**/*') if f.is_file() and f.name.endswith(".ttl") and not f.name.endswith("template.ttl")]
    with open("output.ttl", "w", encoding="utf-8") as outfile:
        print("*** Combining .ttl files . . .")
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


"""
Remove intermediate files, e.g., init, logpai, and ottr files
"""
def remove_intermediates(out_path):
    for path in out_path.glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)


if __name__ == "__main__":
    main()
