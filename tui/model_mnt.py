import re
import logging
import sys
import os

# Set environment variables
os.environ["PYTORCH_CUDA_ALLOC_CONF"]="expandable_segments:True"
os.environ["HF_TOKEN"] = "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"

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)  # Set to ERROR level
logging.getLogger().setLevel(logging.ERROR)  # Ensure root logger is at ERROR level

import torch
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import PromptTemplate
from transformers import AutoTokenizer, logging as hf_logging
from tqdm import tqdm

# Disable tqdm progress bars
tqdm.disable = True

# Suppress HuggingFace and transformers logging output
hf_logging.set_verbosity_error()

# Selected model path or identifier
selected_model = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# Define system prompt
#system_prompt = "You are a Q&A assistant on FrameNet. Your goal is to answer questions as accurately as possible based on the instructions and context provided. Avoid mentioning any unrelated concepts or information related to the user prompt. Strictly adhere to the instructions given by the user."

system_prompt = """You are Chatty AI, a specialized AI chatbot focused on Construction Grammar (CxG) and FrameNet. Your primary knowledge base includes academic research publications on CxG and FrameNet, as well as the FrameNet 1.7 dataset. You aim to assist researchers, linguists, and students with in-depth, accurate, and contextually relevant information.

When responding:

1. Use clear and concise language suitable for an academic audience.
2. Provide definitions, explanations, and overviews of terms, concepts, and theories related to CxG and FrameNet when necessary.
3. If the user question is outside the scope of CxG, FrameNet, or related topics, politely inform them that your specialization is limited to these areas and encourage them to ask about a relevant topic.
4. Suggest related topics or provide general linguistic insights when appropriate.
5. Generate only the requested output and keep it brief also don't repeat the output. Avoid repetition and creating output with gibberish text.

Remain informative, precise, and helpful, always grounding your responses in the provided knowledge base."""

# Define query wrapper prompt
query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")

# Initialize tokenizer
tokenizer = AutoTokenizer.from_pretrained(selected_model)
stopping_ids = [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|eot_id|>")]

# Initialize HuggingFace LLM
llm = HuggingFaceLLM(
    context_window=3584,
    max_new_tokens=1536,
    generate_kwargs={"temperature": 0.1, "do_sample": True},
    system_prompt=system_prompt,
    query_wrapper_prompt=query_wrapper_prompt,
    tokenizer_name=selected_model,
    model_name=selected_model,
    device_map="auto",
    stopping_ids=stopping_ids,
    model_kwargs={"torch_dtype": torch.float16}
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Set cache directory for embeddings
cache_direc = "../embed_model"
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_folder=cache_direc)
#embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2", cache_folder=cache_direc)

from llama_index.core import Settings

# Configure LLM and embedding model settings
Settings.llm = llm
Settings.embed_model = embed_model

from llama_index.readers.json import JSONReader
from llama_index.core import SimpleDirectoryReader

# Load documents
#documents = SimpleDirectoryReader("../frame_and_papers/").load_data()
#documents = SimpleDirectoryReader("../frame_and_papers_compressed/").load_data()
#parser = JSONReader()
#file_extractor = {".json": parser}
#documents = SimpleDirectoryReader("../tmp/", file_extractor=file_extractor).load_data()
documents = SimpleDirectoryReader("../tmp/").load_data()

from llama_index.core import VectorStoreIndex

# Create vector store index from documents
index = VectorStoreIndex.from_documents(documents)

# Initialize chat engine
chat_engine = index.as_query_engine()

def gen_output(prom):
    output = chat_engine.query(prom)
    return output

