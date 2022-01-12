import os
import shlex
import time

"""
Assign IDs to each entity and relation in the KG.
Regenerate the triples using the IDs.
in_path: path to .ttl file to be processed
out_path: path to save the produced .del file
labels: true if .ttl file contains labeled data, false otherwise
"""
def gen_ids(in_path, out_path, labels=False):
    print("*** Generating IDs . . .")
    start = time.time()
    ent_ids = {}
    rel_ids = {}
    lines = []

    with open(in_path) as f:
        content = f.readlines()

        # Skip prefix definitions
        for i in range(len(content)):
            if content[i].startswith("@prefix") or content[i] == "\n":
                continue

            # Make a list of each line, and take out trailing newlines, periods, and semicolons
            lines.append(shlex.split(content[i].rstrip("\n").rstrip(";").rstrip(".")))

        # Commas separating object entities need to be stripped separately to prevent stripping from log messages
        lines = [[j for j in i if j != ","] for i in lines]
        for i in range(100):
            print(lines[i][0])

        ent_count = 0
        rel_count = 0

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
                num_args = len(lines[i]) - 1 if labels else len(lines[i])
                for j in range(num_args):
                    if lines[i][j] not in ent_ids and j > 0:
                        ent_ids[lines[i][j]] = ent_count
                        ent_count += 1

    # If the data is labelled, it must be test data. 
    # Data with no labels must be training data, since it is implicitly labelled as observed
    if labels:
        save_data(os.path.join(out_path, "test.del"), lines, ent_ids, rel_ids, labels=True)
    else:
        save_data(os.path.join(out_path, "train.del"), lines, ent_ids, rel_ids)

    save_ids(os.path.join(out_path, "entity_ids.del"), ent_ids)
    save_ids(os.path.join(out_path, "relation_ids.del"), rel_ids)

    end = time.time()
    print("*** IDs generated in {:.2f}s".format(end - start))


"""
Recreate training/testing data using entity and relation IDs
Output file will be in triple form (e.g., 0 0 1)
path: path to save training data to (should be .del file)
lines: original lines of training data with extra whitespace and symbols removed
ent_dict: dictionary containing mappings of entities to IDs
rel_dict: dictionary containing mapping of relations to IDs
labels: true if the data is labeled (testing data), false otherwise (training data)
"""
def save_data(path, lines, ent_dict, rel_dict, labels=False):
    # Go back through output.ttl, keeping track of the current subject and relation
    # For every object entity in that line, make a new triple
    with open(path, "w") as f:
        for i in range(len(lines)):
            if len(lines[i]) == 1:
                current_sub = ent_dict[lines[i][0]]
                continue

            num_args = len(lines[i]) if not labels else len(lines[i]) - 1
            for j in range(num_args):
                current_rel = rel_dict[lines[i][0]]
                if j > 0:
                    if labels:
                        f.write(str(current_sub) + "\t" + str(current_rel) + "\t" + str(ent_dict[lines[i][j]]) + "\t" + str(lines[i][-1]) + "\n")
                    else:
                        f.write(str(current_sub) + "\t" + str(current_rel) + "\t" + str(ent_dict[lines[i][j]]) + "\n")


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
