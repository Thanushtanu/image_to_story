
import requests
from transformers import pipeline
import streamlit as st
from gradio_client import Client
import os


load_dotenv(find_dotenv())

import re

def extract_dialogue_from_dict_list(text_list):
    if not isinstance(text_list, list):
        raise TypeError("Expected a list of dictionaries")
    
    dialogues = []
    dialogue_keyword = "dialogue:"

    for item in text_list:
        if 'generated_text' in item:
            text = item['generated_text']
            # Find all instances of dialogue in the text
            matches = re.findall(rf"{dialogue_keyword}\s*(.*?)(?=\n|$)", text, re.DOTALL)
            dialogues.extend(matches)

    # Join all dialogues into a single string
    all_dialogues = ' '.join(dialogue.strip() for dialogue in dialogues if dialogue.strip())
    return all_dialogues

def img2text(url):
    img_to_text = pipeline("image-to-text" , model="Salesforce/blip-image-captioning-large")
    text = img_to_text(url)[0]['generated_text']
    #print(text)
    return text


def text_to_text (scenario):
     
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    headers = {"Authorization": "Bearer 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"}

    def query(payload  ):
        print("hi")
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    template = """
        act as a director. write a dialogue for the provided text.
        text : {scenario}
        dialogue:  
    
        """	
    output = query({
        "inputs": template,
         "parameters": {"max_new_tokens": 20} 
    })
    #print(output)
    return output[0]['generated_text']


def  text_to_gpt(scenario):

    text_input = """
        act as a story writer and write a dialogue for the given text in 1 line.
        text : {scenario}
        dialogue:  
    
        """	

    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": "Bearer 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"}
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": text_input,
    })
   
    print(extract_dialogue_from_dict_list(output))
    return extract_dialogue_from_dict_list(output)
                



def txt_to_speech(audio):

    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": "Bearer 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"}
    payloads = {
        "inputs": audio
    }
    response = requests.post(API_URL, headers=headers, json=payloads)
    with open ('audio.flac' , 'wb') as file:
        file.write(response.content)






def main():

    st.set_page_config(page_title="image to audio story" , page_icon="👀")

    st.header("Turn image into audio story")

    uploaded_file = st.file_uploader("choose an image..." , type= "jpg")

    if uploaded_file is not None:
        print(uploaded_file)

        bytes_data = uploaded_file.getvalue()

        with open(uploaded_file.name , "wb") as file:
            file.write(bytes_data)

        st.image(uploaded_file , caption='Uploaded Image.' , use_column_width=True)

        scenario = img2text(uploaded_file.name)

        story = text_to_gpt(scenario)

        txt_to_speech(story)

        with st.expander("Scenario"):
            st.write(scenario)

        with st.expander("Story"):
            st.write(story)    

        st.audio("audio.flac")    

if __name__ == '__main__':
    main()



