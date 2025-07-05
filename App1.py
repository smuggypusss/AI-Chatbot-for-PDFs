import databutton as db
import streamlit as st
import openai
from streamlit_player import st_player
import base64
from PIL import Image
import time
import requests
from my_pdf_lib import get_index_for_pdf
from key_check import check_for_openai_key
import json
from google.cloud import texttospeech as tts
from googleapiclient.discovery import build
from IPython.display import display, HTML
from streamlit_extras.switch_page_button import switch_page


tts_key=db.secrets.get("TTS_KEY")
openai.api_key = db.secrets.get("OPENAI_API_KEY")
subscription_key ="a9739b8eeaf04be2962ab99b746ed99f"
endpoint = "https://api.bing.microsoft.com/"
url=f"{endpoint}v7.0/images/search"
Scrapping = db.secrets.get(name="Scrapping")
new_offset=0

def delete_old_audio():
    db.storage.binary.delete("speech_audio.mp3")
def generate_speech(result,output_file):
    # Replace with the path to your JSON key file
    json_data = db.storage.json.get("websearch-400206-b9b2cb0c0c9a-json", default={})
    json_file_path = "json_key.json"  # Replace with the desired file path
    with open(json_file_path, "w") as json_file:
        json.dump(json_data, json_file)
    # Initialize a client
    client = tts.TextToSpeechClient.from_service_account_file(json_file_path)

    # Create a request
    synthesis_input = tts.SynthesisInput(text=result)

    # Select the voice type and language
    voice = tts.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-D',
        ssml_gender=tts.SsmlVoiceGender.NEUTRAL
    )

    # Configure the audio output
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech conversion
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    # Save the audio to a file
    audio_content=response.audio_content
    db.storage.binary.put(output_file,audio_content)
    

@st.cache_data
def create_vectordb(files):
    with st.spinner("Please Wait"):
        vectordb = get_index_for_pdf(files, openai.api_key)

    return vectordb

@st.cache_data    
def retrieve_pdf_content(pdf_keys):
    return [db.storage.binary.get(key) for key in pdf_keys]
#vectordb with 254 files has already been cretated, will now call and initialize the function with less pdfs
pdf_keys = ["06-maths-ch1-pdf","06-maths-ch2-pdf","06-maths-ch3-pdf","06-maths-ch4-pdf","06-maths-ch5-pdf","06-maths-ch6-pdf","06-maths-ch7-pdf","06-maths-ch8-pdf","06-maths-ch9-pdf","06-maths-ch10-pdf","06-maths-ch11-pdf","06-maths-ch12-pdf","06-maths-ch13-pdf","06-maths-ch14-pdf"
           ]

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
pdf_content = retrieve_pdf_content(pdf_keys)
vectordb = create_vectordb(pdf_content)
def delete_chat_logs():
    db.storage.json.put("chat_logs", [])
def chat_logs_page():
    chat_logs = db.storage.json.get('chat_logs', default=[])
    if len(chat_logs) > 0:
        for index, item in enumerate(chat_logs):
            question = item.get('question', '')
            bot = item.get('bot', '')
            st.write(f"Message {index + 1}:")
            st.write(f"Question: {question}")
            st.write(f"Bot Response: {bot}")
    else:
        st.header("No chat logs available.")

def save_chat_logs(bot_response):
    question = st.session_state.get("current_question")
    chat_log = {"question": question, "bot": bot_response}
    chat_logs = db.storage.json.get('chat_logs', default=[])
    chat_logs.append(chat_log)
    db.storage.json.put('chat_logs', chat_logs)

def update_chat_logs(prompt, response):
    prompt.append({"role": "assistant", "content": response})
    save_chat_logs(response)
def home():
    return

page_selection= st.sidebar.selectbox("Select a page",["Home","Chat History"])

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state["current_question"] = ""
if "prompt" not in st.session_state:
    st.session_state["prompt"] = []
# Execute the selected page
if page_selection == "Home":
    #st.write("Want to have a quick summary of chapters? Try this app.")
    want_to_contribute = st.button("Class Wise query")
    if want_to_contribute:
        switch_page("App2")
    def enable_autoscroll():
        scroll_css = """
        <style>
        .autoscroll {
            overflow-y: scroll !important;
            height: 500px !important;
        }
        </style>
        """
        st.markdown(scroll_css,unsafe_allow_html=True)
    enable_autoscroll()
   
    home()

    prompt_template = """
        You are Ekal's AI assistant 
        You are providing information to a student so explain in simpler
        terms.
        You can also answer questions outside the pdf content
        You are a PDF file expert that combines the knowledge contained
        in a PDF with all of your other training data. It is your job
        to help the user consume the content of that PDF through questions
        and understanding it deeply through providing real-life examples
        and references to relevant other literature and content. 
        Give information in form of bulletin points only not paragraph

        The PDF content is:
        {pdf_extract}
    """
    prompt = st.session_state.get("prompt")

    # Ensure that prompt is not empty
    if not prompt:
        prompt = [{"role": "system", "content": ""}]
    bot_responses = []
    question = st.text_area("Ask anything",height=100)
    if "current_question" not in st.session_state:
        st.session_state["current_question"] = ""
    if "prompt" not in st.session_state:
        st.session_state["prompt"] = []
    if st.button("Send"):
     check_for_openai_key()
    
     # If the user asks a question
     if question:
        st.session_state["current_question"] = question

       
        vectordb = vectordb  

      
        search_results = vectordb.similarity_search(question, k=5)
        pdf_extract = "\n".join([result.page_content for result in search_results])

       
        prompt[0] = {
            "role": "system",
            "content": prompt_template.format(pdf_extract=pdf_extract),
        }

       
        prompt.append({"role": "user", "content": question})

       
        max_context_length = 4097
        prompt_length = sum(len(message["content"]) for message in prompt)
        if prompt_length > max_context_length:
            excess_length = prompt_length - max_context_length
            excess_messages = []
            while excess_length > 0:
                message = prompt.pop(0)
                message_length = len(message["content"])
                if excess_length >= message_length:
                    excess_messages.append(message)
                    excess_length -= message_length
                else:
                    message["content"] = message["content"][:-excess_length]
                    prompt.insert(0, message)
                    excess_length = 0
            excess_message_count = len(excess_messages)
            #st.warning(f"The prompt was truncated to fit within the maximum context length. {excess_message_count} message(s) were removed.")

        
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"), st.markdown("<div class='autoscroll'>"):
            botmsg = st.empty()  
        
        response = []
        result = ""
        for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=prompt, stream=True
        ):
            text = chunk.choices[0].get("delta", {}).get("content")
            if text is not None:
                response.append(text)
                result = "".join(response).strip()
                image_data = db.storage.binary.get(key="classroom-final-jpg")
                #image=Image.open(image_data)
                #botmsg.markdown(f'<div style="background-color: lightgreen; padding: 10px;">{result}</div>', unsafe_allow_html=True) 
                botmsg.info(result)
                #botmsg.image(image,caption=result)
        st.markdown("</div>",unsafe_allow_html=True)
        bot_responses.append(result)
        output_file="output.wav"
        generate_speech(result,output_file)
        audio_file=db.storage.binary.get("output.wav")
        audio_url = f"data:audio/wav;base64,{base64.b64encode(audio_file).decode()}"
        st.markdown(f'<audio src="{audio_url}" autoplay controls></audio>', unsafe_allow_html=True)
        update_chat_logs(prompt, result)
        st.session_state["prompt"] = prompt
        headers={"Ocp-Apim-Subscription-Key":subscription_key}
        params={
            "q":question,
            "license":"public",
            "imageType":"photo",
            "safeSearch":"Strict",
            "count":4,
        }
        contentUrls=[]
        while new_offset is not None and new_offset<=4:
         params["offset"]=new_offset
         response = requests.get(url, headers=headers, params=params)
         response.raise_for_status()
    
         result = response.json()
    
         time.sleep(1)
    
         new_offset = result.get("nextOffset",None)
         for item in result["value"]:        
            contentUrls.append(item["contentUrl"])
        for item in result["value"]:
            st.image(item["contentUrl"], caption="Image")
    if st.button("Show Video Results:"):
      api_key = db.secrets.get('YOUTUBE_API_KEY')
      youtube = build('youtube', 'v3', developerKey=api_key)
      def search_videos(query):
        request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=3)
        response = request.execute()
        return response

      # Search for videos related to the question
      results = search_videos(question)

      # Display the video titles and URLs
      for item in results['items']:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        url = f'https://www.youtube.com/watch?v={video_id}'
        thumbnail_url = item['snippet']['thumbnails']['default']['url']
        st.write(f'Title: {title}')
        st.write(f'URL: {url}')
        st.image(thumbnail_url,caption='Thumbnail')
        display(HTML(f'<video src="{url}" width="640" height="360" controls></video>'))
        st_player(url)
#elif page_selection == "Chat History":
test=st.checkbox("Chat History")
if test:
    if st.button("Delete Chat History"):
        delete_chat_logs()
        st.success("Chat History Deleted")
    chat_logs_page()