from difflib import SequenceMatcher
import re
import pandas as pd
import random

def chartotoken(data):
    testing_json=data.copy()
    tokens=testing_json['sentence'].split() # obtaining tokens
    char_to_token = {}
    current_char = 0
    for i, token in enumerate(tokens):
        for char in token:
            char_to_token[current_char] = i # mapping each character to token
            current_char += 1
        char_to_token[current_char] = i  # For the space after the token
        current_char += 1
    new_list=list() # new frame list
    for i in testing_json["frame annotations"]:
        new_frame=dict()
        new_frame["frame name"]=i["frame name"]
        new_frame["lexical token"]=i["lexical token"]
        new_frame["span"]=[char_to_token.get(i["span"][0],-1),char_to_token.get(i["span"][1],-1)]
        fe_list=list() # new fe list
        for j in i["frame elements"]:
            new_fe=dict()
            new_fe["frame element"]=j["frame element"]
            new_fe["token"]=j["token"]
            new_fe["span"]=[char_to_token.get(j["span"][0],-1),char_to_token.get(j["span"][1],-1)]
            fe_list.append(new_fe)
        new_frame["frame elements"]=fe_list
        new_list.append(new_frame)
    testing_json["frame annotations"]=new_list
    return testing_json # transformed JSON

prompt_test='''"Nowhere is the threat of nuclear war or nuclear terrorism, or the need to safeguard nuclear weapons more important than in South Asia, the home to Al Qaida, who seeks nuclear weapons, Dorgan said describing it as an area where relations among regional nuclear powers - China, India, Pakistan - have historically been tense."'''
def gen_output(pr=prompt_test,t=0.3,max_t=8192):
    ex=str(chartotoken(data['answer'][0])).replace("'",'"')

    messages = [
        {"role": "system", "content": '''You are a FrameNet expert tasked with annotating sentences in JSON format. Your output should strictly adhere to the provided JSON schema.

    **JSON Schema:**
    {
        "sentence": "Original sentence",
        "frame annotations": 
        [{
            "frame name": "Frame name 1",
            "lexical token": "token evoking frame 1",
            "span": [start lexical token index, end lexical token index],
            "frame elements": [
            {"frame element": "frame element 1 role","token": "Frame element text in sentence","span": [start token index, end token index]},
            {"frame element": "frame element 2 role","token": "Frame element text in sentence","span": [start token index, end token index]},
            {"frame element": "frame element 3 role","token": "Frame element text in sentence","span": [start token index, end token index]}]
        },
        {
            "frame name": "Frame name 2",
            "lexical token": "token evoking frame 2",
            "span": [start lexical token index, end lexical token index],
            "frame elements": [
            {"frame element": "frame element 1 role","token": "Frame element text in sentence","span": [start token index, end token index]},
            {"frame element": "frame element 2 role","token": "Frame element text in sentence","span": [start token index, end token index]},
            {"frame element": "frame element 3 role","token": "Frame element text in sentence","span": [start token index, end token index]}]
        }]
    }

**Example:**
For the sentence "Forest fires continue to rage in Spain", the output would be:
```json
'''+f'''{ex}'''},
        {"role": "user", "content": f'''Annotate the following sentence based on FrameNet knowledge, strictly adhering to the provided JSON schema:

{pr}'''},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens=max_t,
        eos_token_id=terminators,
        do_sample=True,
        temperature=t,
        top_p=0.9,
    )

    result=outputs[0]["generated_text"][-1]['content']
    return result


def ex_json(result):
    import re
    import json

    # Regular expression to match the JSON object
    json_pattern = re.compile(r'(\{.*\})', re.DOTALL)
    match = json_pattern.search(result)
    #match = json_pattern.search(result.replace("'",'"'))

    if match:
        json_str = match.group(1)
        # Parse the JSON string
        #json_obj = json.dumps(json.loads(json_str),indent=4)
        json_obj = json.loads(json_str)
        return json_obj
    else:
        return "No JSON object found."

def compare_spans(span_pred, span_true):
    # Calculate the difference in start and end indices
    start_diff = abs(span_pred[0] - span_true[0])
    end_diff = abs(span_pred[1] - span_true[1])
    total_diff = start_diff + end_diff
        
    # Normalize the score to be between 0 and 1 (closer is better)
    span_range = max(span_true[1], span_pred[1],span_true[0], span_pred[0]) - min(span_true[0], span_pred[0],span_true[1], span_pred[1]) + 1
    span_score = max(0, 1 - total_diff / span_range)
    return span_score


def compute_score_mf(prediction, true_answer):
    # Initialize scores list
    scores = []
    
    # Tokenize the sentence
    pred_sentence = prediction['sentence']
    true_sentence = true_answer['sentence']
    
    # Compute sentence similarity
    sentence_score = SequenceMatcher(None, pred_sentence.lower().strip(), true_sentence.lower().strip()).ratio()
    scores.append(sentence_score)
    
    # Extract frame annotations lists
    pred_frames = prediction['frame annotations']
    true_frames = true_answer['frame annotations']
    
    # Iterate through each predicted frame
    frame_scores = []
    for pred_frame in pred_frames:
        # Find the corresponding frame in the true answer
        true_frame = next((f for f in true_frames if SequenceMatcher(None, pred_frame['frame name'].lower().strip(), f['frame name'].lower().strip()).ratio() > 0.5), None)
        #true_frame = next((f for f in true_frames if f['frame name'] == pred_frame['frame name']), None)

        if true_frame:
            # Frame name matches, now check the other attributes
            lexical_token_score = SequenceMatcher(None, pred_frame['lexical token'].lower().strip(), true_frame['lexical token'].lower().strip()).ratio()
            span_score = compare_spans(pred_frame['span'], true_frame['span'])
            #span_score = SequenceMatcher(None, str(pred_frame['span']), str(true_frame['span'])).ratio()
            
            # Initialize frame element scores
            fe_scores = []
            
            # Extract frame elements
            pred_fes = {fe['frame element']: fe for fe in pred_frame['frame elements']}
            true_fes = {fe['frame element']: fe for fe in true_frame['frame elements']}
            
            # Compute scores for each frame element
            for fe_name, true_fe in true_fes.items():
                if fe_name in pred_fes:
                    pred_fe = pred_fes[fe_name]
                    token_score = SequenceMatcher(None, pred_fe['token'].lower().strip(), true_fe['token'].lower().strip()).ratio()
                    fe_scores.append(token_score)
                    span_score_fe = compare_spans(pred_fe['span'], true_fe['span'])
                    #span_score_fe = SequenceMatcher(None, str(pred_fe['span']), str(true_fe['span'])).ratio()
                    fe_scores.append(span_score_fe)
                else:
                    fe_scores.append(0)
            
            # Handle missing predictions in true frame elements
            for fe_name, pred_fe in pred_fes.items():
                if fe_name not in true_fes:
                    fe_scores.append(0)
            
            # Append average frame element score
            if fe_scores:
                avg_fe_score = sum(fe_scores) / len(fe_scores)
            else:
                avg_fe_score = 0
            
            # Calculate overall frame score and append it
            frame_score = (lexical_token_score + span_score + avg_fe_score) / 3
            frame_scores.append(frame_score)
            scores.append(frame_score)
        else:
            # If the frame is missing in the true answer, give it a score of 0
            frame_scores.append(0)
            scores.append(0)
    
    # Average the frame scores and append to the main scores list
    if frame_scores:
        avg_frame_score = sum(frame_scores) / len(frame_scores)
    else:
        avg_frame_score = 0
    
    #scores.append(avg_frame_score)
    
    # Calculate and return the final score
    return sum(scores) / len(scores), avg_frame_score

import transformers
import torch
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

model_id = "../LLMs/llama-models/models/llama3_1/llama-3.1-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

data = pd.read_pickle("bench-fn_data.pkl")
index=random.randrange(1,4993)
question=data["question"][index]
true_answer=data["answer"][index]
true_answer_token=chartotoken(true_answer)

output=gen_output(pr=question[:-57])
pred_json=ex_json(output)
scores=compute_score_mf(pred_json,true_answer_token)

print(f'''Prompt >>> Annotate the following sentence based on FrameNet knowledge, strictly adhering to the provided JSON schema:\n {question[:-57]}''')
print()
print(f'''True Annotation >>>\n {true_answer_token}''')
print()
print(f'''Predicted Annotation >>>\n {pred_json}''')
print()
print(f'''Overall Score >>> {scores[0]} and Average frame Score >>> {scores[1]}.''')