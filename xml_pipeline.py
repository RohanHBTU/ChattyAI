import argparse
from bs4 import BeautifulSoup
import re
import json

def get_fr_name(name):
    with open(name, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    frame_name=Bs_data.find('frame').get('name')
    if len(frame_name)!=0:
        frame_name=frame_name.replace("-"," ").replace("_"," ").strip()
        return frame_name
    else:
        return "no frame name"

def get_fr_def(name):
    with open(name, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    b_unique = Bs_data.find_all('definition')
    if len(b_unique)!=0:
        fr_def=str(b_unique[0]).replace('&lt;','<').replace('&gt;','>')
        min_no=0
        expos=fr_def.find('<ex>')
        if expos==-1:
            expos=214748
        defpos=fr_def.find('</def-root>')
        if defpos==-1:
            defpos=214748
        if min(expos,defpos)==214748:
            min_no=fr_def.find('<def-root>')+11
        else:
            min_no=min(expos,defpos)
        fr_def=fr_def[fr_def.find('<def-root>')+10:min_no].replace('\n',' ').strip()
        fr_def=re.compile(r'<[^>]+>').sub('', fr_def).strip()
        return fr_def
    else:
        return "no frame definition"

def get_fe_def(name):
    with open(name, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    
    fe_unique = Bs_data.find_all('FE')
    if len(fe_unique)!=0:
        for i in range(len(fe_unique)):
            name=fe_unique[i].get('name').replace("-"," ").replace("_"," ").strip()
            value=fe_unique[i].find('definition')
            value=str(value).replace('&lt;','<').replace('&gt;','>')
            marker=value.find('<ex>')
            if marker==-1:
                marker=214748
            value=value[:min(marker,len(value))].replace('\n',' ')
            value=re.compile(r'<[^>]+>').sub('', value).strip()
            yield name,value
    else:
        return "no frame element found","no frame element definition found"

def get_lex_udef(name):
    with open(name, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    
    le_unique = Bs_data.find_all('lexUnit')
    if len(le_unique)!=0:
        for i in le_unique:
            name=str(i.get('name')).replace("-"," ").replace("_"," ").strip()
            value=str(i.find("definition")).replace('&lt;','<').replace('&gt;','>').replace('\n',' ')
            value=re.compile(r'<[^>]+>').sub('', value).strip()
            yield name,value
    else:
        return "no lex unit","no lex unit def"
    
def whole_tag(text,tag,at="name="): #inner content,remaining part, attribute data
    value=text[text.find('>',text.find(f"<{tag}"))+1:text.find(f"</{tag}>")]
    if text.find(at)!=-1:
        att_name=text[text.find(at)+6:text.find('">',text.find(f"<{tag}"))]
    else:
        att_name=""
    return value.strip(),text[text.find(f"</{tag}>")+len(tag)+3:].strip(),att_name.strip()

def get_fr_ex(name):
    with open(name, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    Bs_data=str(Bs_data).replace('&lt;','<').replace('&gt;','>')
    Bs_data = BeautifulSoup(Bs_data, "xml")

    fe_unique=Bs_data.find_all('ex')
    if len(fe_unique)!=-1:
        for i in fe_unique:
            value2=str(i).replace('&lt;','<').replace('&gt;','>').replace('\n',' ')
            example=re.compile(r'<[^>]+>').sub('', value2[4:-5]).strip()
            yield example
            if value2.find('<t>')!=-1:
                frame_rep=value2[value2.find('<t>')+3:value2.find('</t>')].strip()
                yield frame_rep,f"the lexical unit of {get_fr_name(name)}"
            temp=value2
            for j in range(value2.count('<fex')):
                v,temp,att=whole_tag(temp,'fex')
                fele=att.replace('&lt;','<').replace('&gt;','>').replace('\n',' ')
                yield v,fele
    else: 
        return "no example found"
    
def get_fr_rel(name):
    with open(name, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")
    le_unique = Bs_data.find_all('frameRelation')
    joint=" ".join(str(i) for i in le_unique)
    if joint.find('<relatedFrame')!=-1:
        for i in le_unique:
            if len(i.find_all('relatedFrame'))>0:
                _,_,fr_type=whole_tag(str(i),"frameRelation","type=")
                fr_type=fr_type.replace("-"," ").replace("_"," ").strip()
                relation=", ".join(re.compile(r'<[^>]+>').sub('', str(j)).strip() for j in i.find_all('relatedFrame'))
                relation=relation.replace("-"," ").replace("_"," ").strip()
                yield fr_type,relation
    else:
        return "no related frame type","no related frame name"

def xml_parser(name):
    out=dict()
    
    #frame name
    out['frame_name']=get_fr_name(name)
    
    #frame def
    out['frame_def']=get_fr_def(name)
    
    #frame element desc
    fe_dict=dict()
    for i in get_fe_def(name):
        fe_dict[i[0]]=i[1]
    out['fe_def']=fe_dict
    
    #frame lexical unit & def
    le_dict=dict()
    for i in get_lex_udef(name):
        le_dict[i[0]]=i[1]
    out['lexical']=le_dict
    
    #frame examples
    if get_fr_ex(name)=="no example found":
        out['examples']="no example found"
    else:
        ex=""
        fe_dict_in=dict()
        fe_dict_out=dict()
        for i in get_fr_ex(name):
            if type(i)==type("asd") and len(fe_dict_in)>0:
                fe_dict_out[ex]=fe_dict_in
            if type(i)==type("asd"):
                ex=i
                fe_dict_in=dict()
            elif type(i)==type(('a','b','v')):
                fe_dict_in[i[0]]=i[1]
            else:
                out['examples']="no example/error"
                break
        out['examples']=fe_dict_out
    
    #frame relation
    frel_dict=dict()
    for i in get_fr_rel(name):
        frel_dict[i[0]]=i[1]
    out['fr_rel']=frel_dict
    
    return out

def qa_extractor1(name):
    prompt=list()
    response=list()
    parsed_dict=xml_parser(name)
    ex=parsed_dict['examples']
    for i in ex:
        prompt.append(f"{i} Using Frame Semantics, analyze this statement.")
        fr_ex=""
        for j in ex[i]:
            fr_ex+=f"{j} is {ex[i][j]}, "
        fr_ex=fr_ex[:-2]+"."
        fr_ex=fr_ex.capitalize()
        output=f"The frame is of {parsed_dict['frame_name']}. {parsed_dict['frame_def']} Following are the frame elements. {fr_ex} "
        response.append(output.strip())
    return prompt,response

def qa_extractor2(name):
    parsed_dict=xml_parser(name)
    le_list=", ".join(i[:-2] for i in parsed_dict["lexical"])+"."
    inputer=f"Considering the theory of Frame Semantics and its computational implementation, FrameNet, Propose the frame {parsed_dict['frame_name']} that is evoked by lexical units: {le_list}"
    fr_ele=""
    for j in parsed_dict["fe_def"]:
        value=parsed_dict["fe_def"][j].strip(".")
        fr_ele+=f"{j} describes that {value}, "
    fr_ele=fr_ele[:-2]+"."
    fr_ele=fr_ele.capitalize()
    if type(parsed_dict["fr_rel"])==type({"asd":"qwe"}):
        rel_fr=", ".join(parsed_dict["fr_rel"][i].lower() for i in parsed_dict["fr_rel"])+"."
        rel_fr="Related frame(s) is/are "+rel_fr
    else:
        rel_fr="No related frame is present."
    output=f"This frame explains that, {parsed_dict['frame_def']} Following are the description of the frame elements. {fr_ele} {rel_fr}"
    return inputer.strip(),output.strip()

def qa_extractor3(name):
    parsed_dict=xml_parser(name)
    inputer=f"Considering the theory of Frame Semantics, a frame is explained as {parsed_dict['frame_def']} Guess the possible frame and it's frame elements."
    fr_ele=""
    for j in parsed_dict["fe_def"]:
        value=parsed_dict["fe_def"][j].strip(".")
        fr_ele+=f"{j} describes that {value}, "
    fr_ele=fr_ele[:-2]+"."
    fr_ele=fr_ele.capitalize()
    if type(parsed_dict["fr_rel"])==type({"asd":"qwe"}):
        rel_fr=", ".join(parsed_dict["fr_rel"][i].lower() for i in parsed_dict["fr_rel"])+"."
        rel_fr="Related frame(s) is/are "+rel_fr
    else:
        rel_fr="No related frame is present."
    output=f"This definition corresponds to the frame of {parsed_dict['frame_name']}. Following are the description of the frame elements. {fr_ele} {rel_fr}"
    return inputer.strip(),output.strip()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("path",help="enter XML file path")

    args=parser.parse_args()
    path=str(args.path)
    name_xml=path.split("/")[-1][:-4]
    '''
    import os
    from tqdm import tqdm
    xml_folder_name = "/mnt/rds/redhen/gallina/projects/ChattyAI/FramesConstructions/fndata-1.7/frame"
    json_folder_name = "frame_json_parsed"
    if not os.path.exists(json_folder_name):
        os.makedirs(json_folder_name)
    file_names = [file for file in os.listdir(xml_folder_name) if file[-4:] == ".xml"]
    progress_bar = tqdm(total=len(file_names), desc="Parsing")
    for file in file_names:
        with open(f'{json_folder_name}/parsed_{file.replace(".xml",".json")}','w') as outfile:
            json.dump(xml_parser(f'{xml_folder_name}/{file}'),outfile,indent=4)
        progress_bar.update(1)
    progress_bar.close()
    print("Finished")

    '''
    with open(f'parsed_{name_xml}.json','w') as outfile:
        json.dump(xml_parser(path),outfile,indent=4)
        print(f"Successfuly parsed and saved as parsed_{name_xml}.json")
    
    pr_pair1=qa_extractor1(path)
    num_ex=len(pr_pair1[0])
    pr_pair2=qa_extractor2(path)
    pr_pair3=qa_extractor3(path)

    with open(f'prompts_{name_xml}.txt','w') as file:
        file.write(f"Prompt 1: {pr_pair2[0]}")
        file.write("\n")
        file.write(f"Response 1: {pr_pair2[1]}")
        file.write("\n\n")
        file.write(f"Prompt 2: {pr_pair3[0]}")
        file.write("\n")
        file.write(f"Response 2: {pr_pair3[1]}")
        file.write("\n\n")
        for i in range(num_ex):
            file.write(f"Prompt {str(i+3)}: {pr_pair1[0][i]}")
            file.write("\n")
            file.write(f"Response {str(i+3)}: {pr_pair1[1][i]}")
            file.write("\n\n")
        print(f"Saved prompts_{name_xml}.txt")
    with open(f'prompts_{name_xml}.txt','rb+') as file:
        file.seek(-4, 2) 
        file.truncate()
