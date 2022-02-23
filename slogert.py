"""
Script to simplify and extend the use of SLOGERT
Provides interface for running SLOGERT on several config files at once, combing the KGs produced at the end
Also used for converting the entities and relations in the KG into IDs to compress the data
Additionally provides an alias command for rebuilding SLOGERT without running tests, for example to effect changes to config files
"""

import argparse
import os

import util.gen_ids as gen_ids
import util.gen_kg as gen_kg

def main():
    # Define CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", "-u", help="rebuild SLOGERT with Maven to capture changes to config files", action="store_true")
    subparsers = parser.add_subparsers()
    # Arguments for generating KG
    gen_kg_parser = subparsers.add_parser("gen-kg", help="generate one knowledge graph from a set of SLOGERT config files")
    gen_kg_parser.add_argument("--save-temps", "-s", help="saves all temporary files to the output/ directory", action="store_true")
    gen_kg_parser.add_argument("--all", "-a", help="run SLOGERT on all config files", action="store_true")
    gen_kg_parser.add_argument("--files", "-f", nargs="+", help="names of config files to run SLOGERT on")
    gen_kg_parser.add_argument("--outfile", "-o", help="path to output the .ttl file")
    gen_kg_parser.set_defaults(func=gen_kg.gen_kg)

    # Arguments for generating IDs
    gen_ids_parser = subparsers.add_parser("gen-ids", help="convert entities and relations from a generated knowledge graph (.ttl file) to IDs and reconstruct the knowldge graph using those IDs")
    # gen_ids_parser.add_argument("--gen-ids", 
    #                     help="convert entities and relations from a generated knowledge graph (.ttl file) to IDs and reconstruct the knowldge graph using those IDs", action="store_true")
    gen_ids_parser.add_argument("--labels", "-l", help="indicates that the .ttl file contains a label after each triple", action="store_true")
    gen_ids_parser.add_argument("--infile", "-i", required=True, help="path to the .ttl file for which to generate IDs")
    gen_ids_parser.set_defaults(func=gen_ids.gen_ids)

    args = parser.parse_args()

    # If updating SLOGERT, only update, then return
    # Rebuild with Maven, and skip tests, used mainly for capturing changes to config files
    if args.update:
        os.system("mvn install -DskipTests")
        return

    # Call the appropriate function based on the args given
    args.func(args)

if __name__ == "__main__":
    main()
