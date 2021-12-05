"""
Script to simplify the use of SLOGERT
Runs SLOGERT on all config files specified, optionally preserving intermediate files
Also used for rebuilding SLOGERT, for example to effect changes to config files
"""

import argparse
import os
import shutil
from pathlib import Path

def main():
    # Define CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--intermediate", "-i", help="keeps all intermediate files", action="store_true")
    parser.add_argument("--update", "-u", help="rebuild SLOGERT with Maven to capture changes to config files", action="store_true")
    args = parser.parse_args()

    # If updating SLOGERT, only update, then return
    # Rebuild with Maven, and skip tests, used mainly for capturing changes to config files
    if args.update:
        os.system("mvn clean install")
        return

    # Define paths to input, output, and config files
    out_path = Path("output/")
    config = "universal-config.yaml"

    slogert_version = get_slogert_version()

    # Call SLOGERT
    os.system("java -jar target/{0} -c src/test/resources/{1}".format(slogert_version, config))

    if not args.intermediate:
        remove_intermediates(out_path)


"""
Returns the SLOGERT .jar file with dependencies to be used when SLOGERT is called
"""
def get_slogert_version():
    version = [f for f in os.listdir("target/") if f.endswith("with-dependencies.jar")]
    return version[0]


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
