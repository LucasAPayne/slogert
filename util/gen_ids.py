"""
Contains functions for converting entities and relations in a knolwedge graph into IDs to compress the data
Note that these functions work specifically on a .ttl file with triples formatted as:
subject
    relation    object [object . . .]   [label]
    relation    object [object . . .]   [label]
    . . .

Note also that the knowledge graph can also be labelled, as in a testing dataset
"""

import os
import shlex
import time
from pathlib import Path

"""
Assign IDs to each entity and relation in the KG.
Regenerate the triples using the IDs.
args: command line arguments defined in slogert.py
"""
def gen_ids(args):
    print("*** Generating IDs...")
    start = time.time()
    ent_ids = {}
    rel_ids = {}
    lines = []

    ttl_name = args.infile[args.infile.rfind('/')+1:]
    in_path = Path(args.infile[:args.infile.rfind('/')]) 
    ids_exist = False
    id_location = ""

    for root, dirs, files in os.walk(str(in_path)):
        if "entity_ids.del" in files and "relation_ids.del" in files:
            ids_exist = True
            id_location = root

    # If IDs have already been generated for the dataset, load them from files
    # Otherwise, generate the IDs from scratch
    if ids_exist:
        print("IDs already generated")
        # Gather IDs from existing files
        ent_ids = load_ids(os.path.join(id_location, "entity_ids.del"), ent_ids)
        rel_ids = load_ids(os.path.join(id_location, "relation_ids.del"), rel_ids)
        lines = load_content(os.path.join(in_path, ttl_name))
    else:
        path_list = in_path.glob("**/*.ttl")
        ent_count = 0
        rel_count = 0
        for file in path_list:
            lines = load_content(file)

            # Go through each list (line)
            # output.ttl expected to look like
            # subject
            #   relation    list(object)
            #   relation    list(object)
            # ...
            # If the list has only one thing, it must be the subject entity
            # If there are two or more things, the first is the relation and the rest are object entities
            for i in range(len(lines)):
                if len(lines[i]) == 1 and lines[i][0] not in ent_ids:
                    ent_ids[lines[i][0]] = ent_count
                    ent_count += 1
                elif len(lines[i]) > 1:
                    if lines[i][0] not in rel_ids:
                        rel_ids[lines[i][0]] = rel_count
                        rel_count += 1

                    # If data is labeled, last item will be label, so discard
                    num_args = len(lines[i]) - 1 if args.labels else len(lines[i])
                    for j in range(1, num_args):
                        if lines[i][j] not in ent_ids:
                            ent_ids[lines[i][j]] = ent_count
                            ent_count += 1

        end = time.time()
        print("*** IDs generated in {:.2f}s".format(end - start))
        save_ids(os.path.join(in_path, "entity_ids.del"), ent_ids)
        save_ids(os.path.join(in_path, "relation_ids.del"), rel_ids)

    print("****** End of ID generation")

    # If the data is labelled, it must be test data. 
    # Data with no labels must be training data, since it is implicitly labelled as observed
    save_data(os.path.join(in_path, "{0}.del".format(ttl_name.split('.')[0])), lines, ent_ids, rel_ids, labels=args.labels)


"""
Recreate training/testing data using entity and relation IDs
Output file will be in triple form (e.g., 0 0 1)
path: path to save training data to (should be .del file)
lines: original lines of training data with extra whitespace and symbols removed
ent_dict: dictionary containing mappings of entities to IDs
rel_dict: dictionary containing mapping of relations to IDs
labels: true if the data is labeled (testing/validation data), false otherwise (training data)
"""
def save_data(path, lines, ent_dict, rel_dict, labels=False):
    def save_with_labels():
        label_path = os.path.splitext(path)[0] + "_labels.txt"
        # Go back through .ttl file, keeping track of the current subject and relation
        # For every object entity in that line, make a new triple
        with open(path, "w") as data_file, open(label_path, "w") as label_file:
            for i in range(len(lines)):
                if len(lines[i]) == 1:
                    current_sub = ent_dict[lines[i][0]]
                    continue

                num_args = len(lines[i]) - 1
                for j in range(1, num_args):
                    current_rel = rel_dict[lines[i][0]]
                    data_file.write(str(current_sub) + "\t" + str(current_rel) + "\t" + str(ent_dict[lines[i][j]]) + "\n")
                    label_file.write(str(lines[i][-1]) + "\n")
    
    def save_no_labels():
        with open(path, "w") as data_file:
            for i in range(len(lines)):
                if len(lines[i]) == 1:
                    current_sub = ent_dict[lines[i][0]]
                    continue

                num_args = len(lines[i])
                for j in range(1, num_args):
                    current_rel = rel_dict[lines[i][0]]
                    data_file.write(str(current_sub) + "\t" + str(current_rel) + "\t" + str(ent_dict[lines[i][j]]) + "\n")

    print("*** Reconstructing KG using IDs...")
    start = time.time()

    if labels:
        save_with_labels()
    else:
        save_no_labels()
    
    end = time.time()
    print("*** KG reconstructed in {:.2f}s".format(end - start))
    print("****** End of KG reconstruction")


"""
Saves mappings of IDs to strings to a file
path: location to write the file to
dict: dictionary containing mappings of entities or relations to IDs
"""
def save_ids(path, dict):
    # Sort the dictionary by value (outputs list of tuples)
    dict = sorted(dict.items(), key=lambda x : x[1])

    with open(path, "w") as f:
        for i in dict:
            f.write(str(i[1]) + "\t" + str(i[0]) + "\n")


"""
Loads mappings of IDs to strings from a file
path: location of file to read from
dict: dictionary to write mappings to
returns the dict that mappings were written to
"""
def load_ids(path, dict):
    with open(path, "r") as f:
        for line in f:
            content = line.rstrip("\n").split("\t")
            dict[content[1]] = content[0]
    
    return dict

"""
Loads the content of a .ttl file into a list and strips unnecessary content and punctuation
path: path to file from which to load content
"""
def load_content(path):
    with open(path, "r") as file:
        lines = []
        content = file.readlines()

        # Skip prefix definitions
        for i in range(len(content)):
            if content[i].startswith("@prefix") or content[i] == "\n":
                continue

            # Make a list of each line, and take out trailing newlines, periods, and semicolons
            lines.append(shlex.split(content[i].rstrip("\n").rstrip(";").rstrip(".")))

        # Commas separating object entities need to be stripped separately to prevent stripping from log messages
        lines = [[j for j in i if j != ","] for i in lines]

    return lines
