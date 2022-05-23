# SLOGERT v1.0.0-SNAPSHOT

-- **S**emantic **LOG E**xt**R**action **T**emplating (SLOGERT) --

* [General Introduction](#general-introduction)
* [Workflow](#workflow)
  - [Initialization](#initialization)
  - [A1 - Extraction Template Generation](#a1---extraction-template-generation)
  - [A2 - Template Enrichment](#a2---template-enrichment)
  - [A3 - RDFization](#a3---rdfization)
  - [KG Generation Algorithm](#kg-generation-algorithm)
* [Getting Started](#getting-started)
  - [Prerequisites for Running SLOGERT](#prerequisites-for-running-slogert)
  - [Setting up the Project](#setting-up-the-project)
  - [Running SLOGERT](#running-slogert)
  - [Additional Commands](#additional-commands)
* [SLOGERT configurations](#slogert-configurations)
	+ [Main Configuration](#main-configuration)
	+ [I/O Configuration](#io-configuration)

## General Introduction 

SLOGERT aims to automatically extract and enrich low-level log data into an RDF Knowledge Graph that conforms to our [LOG Ontology](https://w3id.org/sepses/ns/log#). It integrates

 - [LogPai](https://github.com/logpai/logparser) for *event pattern* detection and *parameter* extractions from log lines
 - [Stanford NLP](https://stanfordnlp.github.io/CoreNLP/) for *parameter type* detection and *keyword* extraction, and 
 - [OTTR Engine](https://ottr.xyz/#Lutra) for RDF generation. 
 - [Apache Jena](https://jena.apache.org) for RDF data manipulation.

We have tested our approach on text-based logs produced by Unix OSs, in particular: 
  
  - Apache,
  - Kernel,
  - Syslog,
  - Auth, and 
  - FTP logs.

In our latest evaluation, we are testing our approach with the [AIT log dataset](https://zenodo.org/record/4264796), which contains additional logs from non-standard application, such as [suricata](https://suricata-ids.org/) and [exim4](https://ubuntu.com/server/docs/mail-exim4). In this repository, we include a small excerpt of the AIT log dataset in the `input` folder as example log sources.

## Workflow
    
![ ](https://raw.githubusercontent.com/sepses/slogert/master/figures/slogert.jpg)
<p align="center">**Figure 1**. SLOGERT KG generation workflow.</p>     

SLOGERT pipeline can be described in several steps, which main parts are shown in Figure 1 above and will be described as the following: 

#### Initialization

* Load `config-io` and `config.yaml`
* Collect target `log files` from the `input folder` as defined in `config-io`. 
  We assume that each top-level folder within input folder represent a single log source
* Aggregate collected log files into single file.
* Add log-source information to each log lines,
* If log lines exceed the configuration limit (e.g., 100k), split the aggregated log file into a set of `log-files`.
	
*Example results of this step is available in `output/auth.log/1-init/` folder* 

#### A1 - Extraction Template Generation

* Initialize `extraction_template_generator` with `config-io` to register extraction patterns
* For each `log-file` from `log-files`
	* Generate a list of `<extraction-template, raw-result>` pairs using `extraction_template_generator`
	
*NOTE: We use **LogPAI** as `extraction_template_generator`*   
*Example results of this step is available in `output/auth.log/2-logpai/` folder* 

#### A2 - Template Enrichment

*  Load existing `RDF_templates` list
*  Load `regex_patterns` from `config` list for parameter recognition
*  Initialize `NLP_engine` engine 
*  For each `extraction-template` from the list of `<extraction-template, raw-result>` pairs
	* Transform `extraction-template` into an `RDF_template_candidate`
	* if `RDF_templates` does not contain `RDF_template_candidate `
		* **[A2.1 - RDF template generation]**
          * For each `parameter` from `RDF_template_candidate`
              * If `parameter` is `unknown`
                  * **[A2.2 - Template parameter recognition]**
                    *  Load `sample-raw-results` from `raw-results`
                    *  Recognize `parameter` from `sample-raw-results` using `NLP_engine` and `regex_patterns` as `parameter_type`
                    *  Save `parameter_type` in `RDF_template_candidate`
                  * **[A2.2 - end]**		
          * **[A2.3 - Keyword extraction]**
            * Extract `template_pattern` from `RDF_template_candidate`
            * Execute `NLP_engine` engine on the `template_pattern` to retrieve `template_keywords`
            * Add `template_keywords` as keywords in `RDF_template_candidate` 
          * **[A2.3 - end]**
          * **[A2.4 - Concept annotation]**
            * Load `concept_model` containing relevant concept in the domain
            * For each `keyword` from `template_keywords `
                * for each `concept` in `concept_model`
                    * if `keyword` contains `concept`
                        * Add `concept ` as concept annotation in `RDF_template_candidate` 
          * **[A2.4 - end]**
          * add `RDF_template_candidate` to `RDF_templates` list
		* **[A2.1 - end]**

*NOTE: We use **Stanford NLP** as our `NLP_engine`*  
*Example results (i.e., `RDF_templates`) of this step is available as `output/auth.log/auth.log-template.ttl`*

#### A3 - RDFization

* Initialize `RDFizer_engine`
* Generate `RDF_generation_template` from `RDF_templates` list
* for each `raw_result` from `raw_results` list
	* Generate `RDF_generation_instances` from `RDF_generation_template` and `raw_result`
	* Generate `RDF_graph` from `RDF_generation_instances` and `RDF_generation_template` using `RDFizer_engine`

*NOTE: We use **LUTRA** as our `RDFizer_engine`*   
*Example `RDF_generation_template` and `RDF_generation_instances` are available in the `output/auth.log/3-ottr/` folder.*    
*Example results of this step is available in the `output/auth.log/4-ttl/` folder* 

### KG Generation Algorithm
    
<p align="center">
  <img width="460" src="https://raw.githubusercontent.com/sepses/slogert/master/figures/algorithm.png">
</p>
<p align="center"><b>Figure 2</b>. SLOGERT KG generation algorithms.</p>     

For those that are interested, we also provided an explanation of the KG generation in a form of Algorithm as shown in the Figure 2 above.  

## Getting Started
### Prerequisites for running SLOGERT
- Ubuntu or MAC OSX (other operating systems have not been tested)
- [Java 11](https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html) (for Lutra)
- [Apache Maven](https://maven.apache.org/download.cgi)
- [Python 3](https://www.python.org/downloads/)

### Setting up the Project
-  If desired, compile and test this project with `mvn clean install`. However, calling the `slogert.py` script with a missing executable will also compile the project, but without running tests.
-  Create a virtual environment for SLOGERT and activate it. With Anaconda/Miniconda, this can be done with `conda create --name slogert` and `conda activate slogert`.
-  Navigate to the folder containing SLOGERT (`cd path/to/slogert`) and install the necessary Python packages (`pip3 install -r requirements.txt`).
-  Each type of log file to be processed will need a configuration file associated with it (more details in [SLOGERT configurations](#slogert-configurations)).
-  You can set properties for extraction in the config file (e.g., number of loglines produced per file). Examples of config and template files are available on the `src/test/resources` folder (e.g., `auth-config.yaml`for auth log data).
- Example log files can be found in `src/test/input`. To use them, simply copy the directories found there to the `input` folder in the root directory of this repo.

### Running SLOGERT
`slogert.py` is the main script providing for simpler use of SLOGERT, and its CLI comes with several arguments. For a full list of commands and their descriptions, run `python slogert.py -h`, `python slogert.py gen-kg -h`, and `python slogert.py post-process -h`. The primary commands for knowledge graph generation are listed below.
-  `python slogert.py gen-kg -a -o path/to/outfile.ttl` will run SLOGERT on all relevant configuration files (log files in the `input` folder that have associated configuration files in the `src/test/resources` folder). Each `.ttl` file produced will be combined into a single file called `outfile.ttl`.
-  Alternatively, `python slogert.py gen-kg -f logType1-config.yaml logType2-config.yaml` will run SLOGERT for the log files associated with `logType1-config.yaml` and `logType2-config.yaml`.
    - Any number of config files can be listed. Note that these are the names of the config files and not full paths. `slogert.py` currently assumes these files to be located in `src/test/resources`, although this may be configurable in the future.
- The result is produced in the path specified with the `--outfile` or `-o` options.
- The output of each step for each type of log is stored in its own folder in the `output/` directory if the `--save-temps` or `-s` flag is set.

### Additional Commands
Post-processing commands for knowledge graphs are also available. KGs can be reformatted to have one triple per line. The knowledge graph data stored as `.ttl` files can be compressed by assigning each entity and relation an ID, and recreating the KG with the IDs in a `.txt` file. Note that all KGs should be processed with the steps from the previous section before performing these steps. Additionally, labels should be appended to triples in the `.ttl` KGs manually or using an outside tool, if desired. This conversion can be accomplished with the following commands.
- `python slogert.py post-process -i path/to/infile.ttl` will perform post-processing on all `.ttl` KGs in the `path/to/` directory. This will format the KGs as having one triple per line.
  - Optionally, the `-g` flag can be set, which generate IDs for all entities and relations in the directory and recreate the KG as `infile.txt` using those IDs. The ID mappings will be stored as `entity_ids.txt` and `relation_ids.txt`.
    - Note that if the IDs have already been generated, they will be loaded from the files containing the mappings.
    - This approach allows separate KGs to use a common pool of IDs and compresses the data in the KG.
- Adding the `-l` flag, as in `python slogert.py post-process -i path/to/infile.ttl -l` indicates that `infile.ttl` contains labelled triples (e.g., suspicion rankings). This is necessary for correct parsing and recontructing the KG with labels preserved.

## SLOGERT configurations

Slogert configuration is divided into two parts: main configuration `config.yaml` and the input parameter `config-io.yaml`. Note that when a change to a configuration file is made, it is necessary to rebuild SLOGERT. This can be done easily by calling `python slogert.py --update`.

### Main Configuration

There are several configuration that can be adapted in the main configuration file `src/main/resources/config.yaml`. We will briefly describe the most important configuration options here.

* **logFormats** to describe information that you want to extract from a log source. This is important due to the various existing logline formats and variants. Each logFormat contain references to the *ottrTemplate* to build the `RDF_generation_template` for RDFization step.
* **nerParameters** to register patterns that will used by StanfordNLP for recognizing log template parameter types. 
* **nonNerParameters** to register standard regex patterns for template parameter types that can't be easily detected using StanfordNLP. Both *nerParameters* and *nonNerParameters* are contains reference for ottr template generation.
* **ottrTemplates** to register `RDF_generation_template` building block necessary for the RDFization process.


### I/O Configuration

The I/O configuration aim to describe log-source specific information that are not suitable to be added into `config.yaml`. An example of this IO configuration is `src/test/resources/auth-config.yaml` for auth log. We will describe the most important configuration options in the following:

* **source**: the name of source file to be searched for in the input folder.
* **format**: the basic format of the log file, which will be used by `extraction_template_generator` in process A1.
* **logFormat**: types of the logfile. this value of this property should be registered in the `logFormats` within `config.yaml` for SLOGERT to work.
* **isOverrideExisting**: whether SLOGERT should use load `RDF_templates` or to override them.
* **paramExtractAttempt**: how many log lines should be processed to determine the `parameter_type` of a `RDF_template_candidate`. 
* **logEventsPerExtraction**: how many log lines should be processed in a single batch of execution. 
