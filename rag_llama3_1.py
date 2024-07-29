import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import torch
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import PromptTemplate

selected_model = "./LLMs/llama-models/models/llama3_1/llama-3.1-8B-Instruct-hf"
#selected_model = "meta-llama/Meta-Llama-3-8B-Instruct"
#selected_model = "meta-llama/Meta-Llama-3-8B"

from llama_index.core import PromptTemplate
system_prompt = "You are a Q&A assistant on FrameNet. Your goal is to answer questions as accurately as possible based on the instructions, conversation history and context provided."
# This will wrap the default prompts that are internal to llama-index
query_wrapper_prompt = PromptTemplate(
    '''<|begin_of_text|><|start_header_id|>system<|end_header_id|>

'''+system_prompt+'''<|eot_id|><|start_header_id|>user<|end_header_id|>

{query_str}<|eot_id|><|start_header_id|>assistant<|end_header_id|>''')

from transformers import AutoTokenizer
from llama_index.llms.huggingface import HuggingFaceLLM
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")
#tokenizer = AutoTokenizer.from_pretrained(selected_model)

stopping_ids = [tokenizer.eos_token_id,tokenizer.convert_tokens_to_ids("<|eot_id|>")]

llm = HuggingFaceLLM(
    context_window=4096,
    max_new_tokens=2048,
    generate_kwargs={"temperature": 0.85, "do_sample": True},
    #system_prompt=system_prompt,
    query_wrapper_prompt=query_wrapper_prompt,
    tokenizer_name=selected_model,
    model_name=selected_model,
    device_map="auto",
    stopping_ids=stopping_ids,
    # change these settings below depending on your GPU
    model_kwargs={"torch_dtype": torch.float16,"load_in_8bit": True},
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

cache_direc="./embed_model"
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5",cache_folder=cache_direc)

from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model

from llama_index.core import SimpleDirectoryReader

# load documents
documents = SimpleDirectoryReader("./frame_and_papers/").load_data()

from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()

wrapper=""
while True:
    inp=input(">> Enter the prompt: ") #"What are the data driven approaches to Framenet expansion?"
    response = query_engine.query(wrapper+inp)
    print(">> Response: ",response)
    wrapper+=inp+"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"+str(response)+"<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
