import argparse
from bs4 import BeautifulSoup
import re
import json

def layer_bifurcator(ann,layer_json,lname,text_bs,layer_bs):
    output1=list()
    labels=layer_bs.find_all('label')
    if len(labels)!=0:
        for label in labels:
            try:
                fname=str(ann.get('frameName'))
                lu=str(ann.get('luName'))
                name=str(label.get('name'))
                start=int(label.get('start'))
                end=int(label.get('end'))
                output1.append([start,end,name,str(text_bs)[start:end+1],fname,lu])
            except:
                continue
        try:
            if type(layer_json[lname])==type(['l']):
                return layer_json[lname]+output1
        except:
            return output1
    else:
        try:
            if type(layer_json[lname])==type(['l']):
                return layer_json[lname]
        except:
            return "empty layer/no label found"

def full_text_anno_parser(name):
    import re
    from bs4 import BeautifulSoup
    if name[-4:]==".xml":
        with open(name, 'r') as f:
            data = f.read()
    else:
        with open(f'/kaggle/input/framenet/framenet_v17/framenet_v17/fulltext/{name}.xml', 'r') as f:
            data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    
    fe_unique = Bs_data.find_all('sentence')
    output_list=list()
    output_json=dict()
    #print(len(fe_unique))
    if len(fe_unique)!=0:
        for i in range(len(fe_unique)):
            text=str(fe_unique[i].find('text'))
            text=re.compile(r'<[^>]+>').sub('', text)
            annotations=fe_unique[i].find_all('annotationSet')
            layer_json=dict()
            for ann in annotations:
                layers=ann.find_all('layer')
                #Bs_data.find_all('sentence')[0].find_all('layer')[0]
                for layer in layers:
                    lname=str(layer.get('name'))
                    result=layer_bifurcator(ann,layer_json,lname,text,layer)
                    layer_json[lname]=result
            out_json=dict()
            out_json[text]=layer_json
            yield out_json
    else:
        return {"no sentence found":"no sentence annotation found"}

def qa_extractor1(pather):
    question=list()
    answer=list()
    for i in full_text_anno_parser(pather):
                #print(i,'\n')
                for j in i:
                    try:
                        prompt=j
                        if prompt[-1]=='.':
                            prompt+=" annotate this sentence considering the frame semantics."
                        else:
                            prompt+=". annotate this sentence considering the frame semantics."
                        response="The given sentence is annotated as follows."
                        for k in i[j]['Target']:
                            response+=f' The frame {k[4]} is evoked by {k[3]} where '
                            for fein in i[j]['FE']:
                                if fein[4]==k[4]:
                                    response+=f"{fein[3]} depicts {fein[2]}, "
                            if response.strip().split()[-1]!='where':
                                response=response[:-2]+'.'
                            else:
                                response=" ".join(response.strip().split()[:-1])+'.'
                        question.append(prompt)
                        answer.append(response)
                    except:
                        continue
    return question,answer

def qa_extractor2(pather):
    question=list()
    answer=list()
    for i in full_text_anno_parser(pather):
                #print(i,'\n')
                for j in i:
                    try:
                        prompt=j
                        if prompt[-1]=='.':
                            prompt+=" annotate this sentence based on named entity recognition."
                        else:
                            prompt+=". annotate this sentence considering the frame semantics."
                        response="The given sentence is annotated as follows. Here,"
                        for k in i[j]['NER']:
                            response+=f" {k[3]} represents {k[2]}, "
                        response=response[:-2]+'.'
                        question.append(prompt)
                        answer.append(response)
                    except:
                        continue
    return question,answer

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("path",help="enter full text annotation XML file path")

    args=parser.parse_args()
    path=str(args.path)
    name_xml=path.split("/")[-1][:-4]

    with open(f'parsed_anno_{name_xml}.json','w') as outfile:
        res_dict=dict()
        count=1
        res_dict['0']={"sample sentence":{"sample layer":[['start','end','label name','highlighted string','frame name(if frame layer)','lexical unit(if frame layer)']]}}
        for i in full_text_anno_parser(path):
            res_dict[str(count)]=i
            count+=1
        json.dump(res_dict,outfile,indent=4)
        print(f"Successfuly parsed and saved as parsed_anno_{name_xml}.json")
    
    pr_pair1=qa_extractor1(path)
    num_ex1=len(pr_pair1[0])
    pr_pair2=qa_extractor2(path)
    num_ex2=len(pr_pair2[0])
    
    with open(f'prompts_anno_fe_{name_xml}.txt','w') as file:
        for i in range(num_ex1):
            file.write(f"Prompt {str(i+1)}: {pr_pair1[0][i]}")
            file.write("\n")
            file.write(f"Response {str(i+1)}: {pr_pair1[1][i]}")
            file.write("\n\n")
        print(f"Saved prompts_anno_fe_{name_xml}.txt")
    with open(f'prompts_anno_fe_{name_xml}.txt','rb+') as file:
        file.seek(-4, 2) 
        file.truncate()
    
    with open(f'prompts_anno_ner_{name_xml}.txt','w') as file:
        for i in range(num_ex2):
            file.write(f"Prompt {str(i+1)}: {pr_pair2[0][i]}")
            file.write("\n")
            file.write(f"Response {str(i+1)}: {pr_pair2[1][i]}")
            file.write("\n\n")
        print(f"Saved prompts_anno_ner_{name_xml}.txt")
    with open(f'prompts_anno_ner_{name_xml}.txt','rb+') as file:
        file.seek(-4, 2) 
        file.truncate()