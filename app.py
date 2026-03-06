import streamlit as st
import requests
import time
import base64
from PIL import Image
from io import BytesIO

class NanoBananaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # Updated to the official endpoint structure
        self.base_url = 'https://api.nanobananaapi.ai/api/v1/nanobanana'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def encode_image(self, uploaded_file):
        """Encodes to Base64 and adds the required Data URI prefix."""
        b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        # Most 3rd party APIs require the data:image prefix to recognize the string as an image
        return f"data:image/jpeg;base64,{b64}"

    def generate_image(self, prompt, images_b64):
        data = {
            'prompt': prompt,
            'type': 'IMAGETOIMAGE', 
            'numImages': 1,
            'imageUrls': images_b64  # This is a list of [pose, face, cloth]
        }
        
        response = requests.post(f'{self.base_url}/generate', headers=self.headers, json=data)
        
        # DEBUG: Check if response is actually JSON before parsing
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
            
        try:
            result = response.json()
        except ValueError:
            raise Exception(f"API returned invalid JSON: {response.text[:100]}")
        
        if result.get('code') != 200:
            raise Exception(f"Generation failed: {result.get('msg', 'Unknown error')}")
        
        return result['data']['taskId']

    def get_task_status(self, task_id):
        response = requests.get(
            f'{self.base_url}/record-info?taskId={task_id}',
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return response.json()

# --- Streamlit UI ---
st.set_page_config(page_title="Nano Banana Studio", page_icon="🍌")
st.title("🍌 Nano Banana Influencer Studio")

with st.sidebar:
    api_key = st.text_input("API Key", type="password")

col1, col2 = st.columns(2)

with col1:
    p_file = st.file_uploader("Pose Image", type=['jpg','png'])
    f_file = st.file_uploader("Face Image", type=['jpg','png'])
    c_file = st.file_uploader("Cloth Image", type=['jpg','png'])
    prompt_txt = st.text_area("Prompt", "A fashion influencer in Paris")
    
    if st.button("Generate"):
        if not api_key or not all([p_file, f_file, c_file]):
            st.error("Missing API Key or Images")
        else:
            api = NanoBananaAPI(api_key)
            try:
                with st.spinner("Processing..."):
                    # Encode all 3 images with prefixes
                    imgs = [api.encode_image(p_file), api.encode_image(f_file), api.encode_image(c_file)]
                    
                    task_id = api.generate_image(prompt_txt, imgs)
                    st.info(f"Task Started: {task_id}")
                    
                    # Polling
                    finished = False
                    while not finished:
                        status = api.get_task_status(task_id)
                        flag = status.get('successFlag')
                        
                        if flag == 1:
                            url = status.get('response', {}).get('resultImageUrl')
                            st.image(url)
                            finished = True
                        elif flag in [2, 3]:
                            st.error(f"Failed: {status.get('errorMessage')}")
                            finished = True
                        time.sleep(4)
            except Exception as e:
                st.error(f"Critical Error: {e}")
