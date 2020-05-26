# SLOGERT v0.8.0-SNAPSHOT

-- **S**emantic **LOG E**xt**R**action **T**emplating (SLOGERT) --

- [SLOGERT v0.8.0-SNAPSHOT](#slogert-v080-snapshot)
  * [General Introduction](#general-introduction)
  * [What does SLOGERT do?](#what-does-slogert-do-)
    + [A0. Log data pre-processing](#a0-log-data-pre-processing)
    + [A1. LOGPAI execution (\*.log to \*.csv)](#a1-logpai-execution----log-to---csv-)
    + [A2. SLOGERT execution (\*.csv to \*.ottr)](#a2-slogert-execution----csv-to---ottr-)
    + [A3. LUTRA execution (\*.ottr to \*.RDF)](#a3-lutra-execution----ottr-to---rdf-)
    + [A4. Background Knowledge Building](#a4-background-knowledge-building)
    + [A5. Knowledge Graph Integration](#a5-knowledge-graph-integration)
  * [Scenario execution](#scenario-execution)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


## General Introduction 

The SLOGERT approach aims to automatically extract and enrich low-level log data into an RDF Knowledge Graphs that conform to our [LOG ontology](https://w3id.org/sepses/ns/log#). Currently we have tried and tested our approach on the text-based logs produced by Unix OS, which includes the following logs: Apache, Kernel, Syslog, Auth, and FTP logs.

Technology-wise, we utilise (i) [LOGPAI](https://github.com/logpai/logparser) for *patterns* detection and *parameter* extractions from log lines, [Standord NLP](https://stanfordnlp.github.io/CoreNLP/) for *parameter type* detection and *keyword* extractions, and [OTTR Engine](https://ottr.xyz/#Lutra) for RDF generation. Furthermore, we also use [Apache Jena](https://jena.apache.org) for RDF data manipulation.

Unfortunately, we didn't manage to combine *LogPai*, *SLOGERT*, and *OTTR Engine* seamlessly for now, and therefore, to use SLOGERT, you will need to do it in several steps. Furthermore, a little bit of log pre-processing is necessary to make sure that we can capture the information about the log source. We will explain the steps in the following section.

## What does SLOGERT do?

Here, we detailed the steps on how to SLOGERT works. The main steps is shown in the Figure 1 below.

![ ](https://raw.githubusercontent.com/sepses/slogert/master/data/slogert.png)
<p align="center">**Figure 1**. The SLOGERT overview figure.</p>

### A0. Log data pre-processing

In this step, we mainly wanted to add information about the logfile source host, i.e., the identification of the host/device that produce the log. We did this since such information can be easily retrieved but not always available in the log data. However, we realise this step is quite trivial and might depends on each use case. Therefore, we didn't include it as part of the main SLOGERT software.

For our sample scenario use case, we have created a small program that would do this pre-processing step plus integrating several logs of the same type (e.g., syslog) into a single file. We called it `slogert-logpai` and you can find it [here](https://github.com/sepses/slogert-logpai).

**input**:    
- `data/_raw-log/<filename>.log`: the raw input of a log. 

**output**:   
- `data/A1_logpai-input/<filename>.log`: the raw log file with an additional first column which identify log source hostname.

### A1. LOGPAI execution (\*.log to \*.csv)

Here, run LOGPAI extraction using the Drain algorithm as suggested in the LOGPAI website based on their benchmarking report. A set of python configuration files as input for LogPai are also provided in the data folder.

LOGPAI will produce two types of results: ```<filename>\_structured.csv```, which is the logline representation in CSV with reference to the log patterns and detected parameters, and the ```<filename>\_template.csv```, which is the log patterns detected by LOGPAI.

**input**:     
- `data/A1_logpai-input/<filename>.log`: enhanced raw log data    
- `data/A1_logpai-input/<filename>.py`: LOGPAI configuration files

**output**:    
- `data/A1_logpai-output/<filename>\_structured.csv`: loglines in csv forms with template id and parameters    
- `data/A1_logpai-output/<filename>\_template.csv`: logline templates as detected by LOGPAI

### A2. SLOGERT execution (\*.csv to \*.ottr)

In this step, we start the main process of templates and parameters annotation.
To this end, we need the output from A1 plus several configuration files, one (`data/config.yaml`) that contains mapping of log data the OTTR template and the LOG/LOGEX ontologies and another one (`data/config-io.yaml`) to describe all inputs and outputs of the SLOGERT execution. 

**input**:     
- `data/A1_logpai-output/<filename>\_structured.csv`: see A1 output above     
- `data/A1_logpai-output/<filename>\_template.csv`: see A1 output above    
- `data/A2_slogert-input/log.ttl`: LOG ontology    
- `data/A2_slogert-input/logex.ttl`: log extraction (LOGEX) ontology    
- `data/A2_slogert-input/config.yaml`: internal configuration and link to LOG and LOGEX ontologies    
- `data/A2_slogert-input/<filename>-config.yaml`: I/O configuration    

**output**:    
- `data/A2_slogert-output/<filename>-base.ottr`: OTTR templates    
- `data/A2_slogert-output/<filename>.ottr`: OTTR instances     


### A3. LUTRA execution (\*.ottr to \*.RDF)

Here, we utilise the LUTRA jar file (v0.6.3) to transform the OTTR instances into RDF. We observe that lutra has limitation for processing large batch of loglines, so we split large(r) files into a batch of 25k log lines for lutra processing.

**input**:     
- `data/A2_slogert-output/<filename>-base.ottr`: OTTR templates    
- `data/A2_slogert-output/<filename>.ottr`: OTTR instances     

**output**:     
- `data/A3_lutra-output/<filename>.ttl`: RDF instances conformed to LOG ontologies.


### A4. Background Knowledge Building

We manually build a background knowledge graph for our evaluation purpose. The idea is that later on, we should be able to automatically generate such background knowledge based on network topology and other information that we can gather from domain experts. 

The knowledge should contains additional *context* information about the observed log data, e.g., temporal relations between persons, users and devices represented in log data. For now, however, we just provided examples using RDF star representation. 

* output: 
- `data/A4_background-KG/ns-slogert.ttls`: OTTR instances     


### A5. Knowledge Graph Integration

In this step, we integrated all knowledge graphs and ontologies into a single repositories for querying. We provide a dump file that you can reuse as well as link to the SPARQL endpoint.

**input**:     
- `data/A2_slogert-input/log.ttl`: LOG ontology    
- `data/A2_slogert-input/logex.ttl`: log extraction (LOGEX) ontology    
- `data/A3_lutra-output/<filename>.ttl`: RDF instances conformed to LOG ontologies.    
- `data/A4_background-KG/ns-slogert.ttls`: OTTR instances    
- `data/port-service-list/port-service.ttl`: port-service-list    

**output**:      
- `https://128.131.169.162:7200/repositories/sepses-transformed`: SPARQL endpoint

 

       
## Scenario execution 

Well, in case you wanted to try it out yourself, or using your own logfiles, feel free to try out the following steps: 

* Run LogPai to generate `<logname>_structured.csv` and `<logname>_templates.csv`. Examples of such files (already enhanced with additional column for hostname) are available on the `scenario/input` folder.  
*  Compile this project (`mvn clean install`)
*  You can set properties for extraction in the config file (e.g., number of loglines produced per file). Examples of config and template files are available on the `src/test/resources` folder (e.g., `auth-config.yaml`for auth log data). 
*  Transform the CSVs into OTTR format using config file. By default, the following script should work to work on the example file. (```java -jar target/slogert-0.8.0-SNAPSHOT-jar-with-dependencies.jar -c src/test/resources/auth-config.yaml```)
*  After the transformation finished, it will provide you with the command to execute lutra, such as the following: (``` java -jar exe/lutra.jar --library scenario/output/auth-base.ottr --libraryFormat stottr --inputFormat stottr scenario/output/auth.ottr --mode expand --fetchMissing > scenario/output/auth.ttl```) 
*  Execute the transformation of the OTTR files into RDF graph using the command above from command line. 

A script for executing transformation data for scenario has been created in the scenario folder `scenario/scenario.sh`. To run it, after you compile the project (`mvn clean install`), run `./scenario/scenario.sh` from project folder.

           
<!--## References
[[1]](#1)
<a id="1">[1]</a> 
Dijkstra, E. W. (1968). 
Go to statement considered harmful. 
Communications of the ACM, 11(3), 147-148.-->