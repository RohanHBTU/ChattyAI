import pandas as pd

data = pd.read_pickle("bench-fn_data.pkl")

#print(data['answer'][0])

import transformers
import torch
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

model_id = "../LLMs/llama-models/models/llama3_1/llama-3.1-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16, "load_in_8bit": True},
    device_map="auto",
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]



messages = [
    {"role": "system", "content": f'''You are an expert on annotating sentences based on FrameNet. Your goal is to answer prompts as accurately as possible based on the instructions provided like annotating sentences in the form of JSON based on framenet knowledge. Refer to this example for following the structure of JSON to be generated by annotating the given sentence, example: "Forest fires continue to rage in Spain". Annotate this sentence considering the frame semantics. JSON: {str(data['answer'][0])} '''},
    {"role": "user", "content": '''"Several forest fires which have ruined well over ten thousand hectares of land are continuing to burn in the Spanish region of Galicia today .". Annotate this sentence considering the frame semantics.'''},
]

outputs = pipeline(
    messages,
    max_new_tokens=8192,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.15,
    top_p=0.9,
)
print()
print("Response: >>>")
print(outputs[0]["generated_text"][-1]['content'])

