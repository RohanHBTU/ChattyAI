# Chatty AI GSoC 2024

## Overview

The [Google Summer of Code (GSoC)](https://summerofcode.withgoogle.com/) 2024 project "Chatty AI" is contributed by [Rohan Kumar Singh](https://github.com/RohanHBTU) with [Red Hen Lab](https://www.redhenlab.org/home).

To get the insight into the work being done or already implemented, read my weekly [blog](https://medium.com/@rohank587/spending-the-summer-24-in-gsoc-with-red-hen-lab-5c8aade49026) or mail me at [rohank587@gmail.com](mailto:rohank587@gmail.com?subject=[GitHub]%20Source%20Han%20Sans) for any queries.

## Table of Contents

- [Installation](#installation)
- [FrameChat](#framechat)
- [Frame Annotation Evaluation](#frame-annotation-evaluation)
- [Fulltext Annotation Parser](#fulltext-annotation-parser)
- [FrameNet XML Parser](#framenet-xml-parser)
- [RAG for Llama3 Instruct](#rag-for-llama3-instruct)
- [Downloading Llama3 Instruct (Meta AI)](#downloading-llama3-instruct)

## Installation

Follow the instructions to setup environment.

Modules to load on CWRU HPC:
- Python/3.11.3-GCCcore-12.3.0

```bash
# Cloning the repository
git clone https://github.com/RohanHBTU/ChattyAI
cd ChattyAI

# [Optional] Creating virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Download dependencies
pip install -r requirements.txt

# Setup Huggingface API key
touch .env
# Enter your Huggingface API key in ".env" like this:
# HUGGINGFACE_API_KEY="..."
```

## FrameChat

### Introduction

This is a terminal application built for CWRU HPC to assist researchers, educators, and students in the fields of Construction Grammar and FrameNet. Users can use this as a tool to tinker with frames and ask several queries related to it.

### Prerequisites

1. Basic installation mentioned in [Installation](#installation).
2. Setup FrameNet dataset.
    - Copy the FrameNet dataset folder `frame/` to the work directory.
    - Create JSON-format FrameNet dataset folder `frame_and_papers/` using [FrameNet XML Parser](#framenet-xml-parser).
    - Paste the research papers available in FrameNet dataset folder into `frame_and_papers/`.
    - (Optional) Combine all indiviual FrameNet files into a single JSON frame file.
3. Request an interactive job on the GPU node of CWRU HPC.

### Usage

The program can be run using

```bash
# Change Directory to tui (Terminal user interface)
cd tui

# Execute the python application
python3 cur_mnt.py
```

#### Key Bindings

When in Frame Blender interface:

- `Tab`: Switch focus between Input and Output windows
- `Enter`: To add newline
- `Ctrl+g`: To reset long context
- `Arrow Keys`: Left/Right in Input Window and Up/Down in Output Window
- `Ctrl+a`: To annotate a sentence prompt
- `Ctrl+t`: To toggle between Short and Long context modes
- `Ctrl+r`: To send the input
- `Ctrl+f`: To get the frame details prompt
- `Ctrl+e`: To exit the application
- `Ctrl+c`: (Only applicable when query in process) to terminate the application

## Frame Annotation Evaluation

This evaluation aims to assess the performance of LLaMA 3 and LLaMA 3.1 8B Instruct models under RAW settings and with Retrieval-Augmented Generation (RAG) applied. The bench-fn_data.pkl file contains examples from the full-text annotation dataset of UC Berkeley, which are used in this evaluation. The Python scripts for evaluating these annotated examples can be found in the evaluation_bench_anno directory.
```bash
#Activate the virtual environment
source .venv/bin/activate

# RAW Llama 3 8B Instruct
python3 eval_llama3_raw.py

# RAW Llama 3.1 8B Instruct
python3 eval_llama3_1_raw.py

# RAG Llama 3 8B Instruct
python3 eval_rag_llama3.py

# RAG Llama 3.1 8B Instruct
python3 eval_rag_llama3_1.py

#leaving virtual environment
deactivate
```

The evaluation process consists of the following steps:

1. **Random Selection of an Example:**  
   The Python script randomly selects an example from the `bench-fn_data.pkl` file.

2. **Annotated JSON Generation:**  
   The selected example is annotated using the Large Language Model (LLM).

3. **Scoring with a Custom Metric:**  
   The generated annotated JSON object is compared against the true annotation using a custom metric function to evaluate the model's performance.

4. **Output:**  
   For each evaluated example, the script prints the following:
   - The **prompt** used for generating the annotation.
   - The **generated annotation** by the LLM.
   - The **true annotation** from the dataset.
   - The **scores** calculated based on the custom metric.

## Fulltext Annotation Parser

### Introduction

This code is capable of converting the original Fulltext annotated corpus of FrameNet data in XML format to JSON format. A single sentence is annotated into various layers such as part of speech, named entity recognition, white space layer (word sense disambiguation), FrameNet layer and others (Other, Sent, Verb). The most significant layers for our purpose are FrameNet and Named Entity Recognition. It is similar to FrameNet XML Parser.

### Usage

```bash
#Activate the virtual environment
source .venv/bin/activate

#Pass XML annotated file path as argument
python3 fulltext_anno_pipeline.py ANC__110CYL068.xml

#leaving virtual environment
deactivate
```
OR
```python
from fulltext_anno_pipeline import full_text_anno_parser

# Example of parsing a directory of .xml files
path = "ANC__110CYL068.xml" #or any other xml annotated file path

#initializing output JSON
res_dict=dict()
count=1

#sample addition for description
res_dict['0']={"sample sentence":{"sample layer":[['start','end','label name','highlighted string','frame name(if frame layer)','lexical unit(if frame layer)']]}}

for i in full_text_anno_parser(path):
	res_dict[str(count)]=i
        count+=1
print(res_dict)
```

## FrameNet XML Parser

### Introduction

This code transforms the original FrameNet data in XML format to JSON format, extracting only important information for frame analysis. This whole parser is available to use as a pipeline in command line interface which also generates some prompt response pairs related to frame analysis based on the frame passed as an argument.

### Usage

```bash
#Activate the virtual environment
source .venv/bin/activate

#Pass XML Frame file path as argument
python3 xml_pipeline.py Exercising.xml

#leaving virtual environment
deactivate
```
OR
```python
from xml_pipeline import xml_parser

# Example of parsing a directory of .xml files
path = "Exercising.xml" #or any other xml frame file path

output_json = xml_parser(path)
print(output_json)
```

## RAG for Llama3 Instruct

### Introduction

This code utilizes Llama3-8B-Instruct-chat locally on CWRU HPC, and achieves Retrieval Augmented Generation (RAG) leveraging Llama-index and performs multi-turn conversation. Specifically, a parser is used to read all the JSON-format FrameNet frame data and a collection of research papers on Construction Grammar (CxG) and FrameNet, and create a query engine with vector store index for querying. Feel free to explore the codebase. 

>**Requires**: A GPU node, Llama3 model locally and a directory of frame_and_papers containing JSON format frames and related papers.

### Usage

```bash
#Activate the virtual environment
source .venv/bin/activate

#Embedding model cache
mkdir embed_model

#Initiating conversation with Llama3
python3 rag_llama3.py

>> Enter the prompt: ...
>> Response : ...

.
.
.

#leaving virtual environment
deactivate
```

## Downloading Llama3 Instruct

Referring to [Llama3's](https://github.com/meta-llama/llama3) Github Repository. A very helpful [guide](https://github.com/meta-llama/llama-recipes/blob/main/recipes/quickstart/Running_Llama3_Anywhere/Running_Llama_on_HF_transformers.ipynb) on Llama3 by Meta.

0. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # enter the virtual environment
```
1. Download dependencies
```bash
pip install -r requirements.txt
```
2. Download the model 

Request download access to Llama 3 [here](https://llama.meta.com/llama-downloads)

```bash
git clone https://github.com/meta-llama/llama3.git
cd llama3
./download.sh # requires the pre-signed URL from Meta License
```
3. Convert the model weights to run with Hugging Face
```bash
# in the llama/ directory
# convert llama weights to huggingface format to make it compatible with HF class
TRANSFORM=`python -c "import transformers;print('/'.join(transformers.__file__.split('/')[:-1])+'/models/llama/convert_llama_weights_to_hf.py')"`
pip install protobuf && python $TRANSFORM --input_dir ${path_to_meta_downloaded_model} --output_dir ${path_to_save_converted_hf_model} --model_size 8B --llama_version 3
```
4. Write Python scripts and run the model
```bash
python3 main.py
```

