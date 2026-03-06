import streamlit as st
import requests
import time
import base64
from PIL import Image
from io import BytesIO

# --- API Wrapper Class ---
class NanoBananaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # Note: Updated to the correct URL from your snippet
        self.base_url = 'https://api.nanobananaapi.ai/api/v1/nanobanana'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def encode_image(self, uploaded_file):
        """Helper to convert uploaded file to base64 for the API."""
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_image(self, prompt, pose_b64, face_b64, cloth_b64):
        """
        Sends multimodal images to Nano Banana. 
        Using 'IMAGETOIMAGE' type as per standard multimodal wrappers.
        """
        data = {
            'prompt': prompt,
            'type': 'IMAGETOIMAGE', 
            'numImages': 1,
            # Passing images as base64 strings in the imageUrls list
            'imageUrls': [pose_b64, face_b64, cloth_b64]
        }
        
        response = requests.post(f'{self.base_url}/generate', headers=self.headers, json=data)
        result = response.json()
        
        if not response.ok or result.get('code') != 200:
            raise Exception(f"Generation failed: {result.get('msg', 'Unknown error')}")
        
        return result['data']['taskId']

    def get_task_status(self, task_id):
        response = requests.get(
            f'{self.base_url}/record-info?taskId={task_id}',
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return response.json()

# --- Streamlit UI ---
st.set_page_config(page_title="Nano Banana Influencer Studio", page_icon="🍌", layout="wide")

st.title("🍌 Nano Banana Influencer Studio")
st.markdown("Generate high-end AI influencers using Pose, Face, and Clothing references.")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Nano Banana API Key", type="password")
    st.divider()
    st.info("This app uses a Task-based polling system for generation.")

# Layout Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload References")
    pose_img = st.file_uploader("1. Pose Reference", type=['png', 'jpg', 'jpeg'])
    face_img = st.file_uploader("2. Face Identity", type=['png', 'jpg', 'jpeg'])
    cloth_img = st.file_uploader("3. Clothing Reference", type=['png', 'jpg', 'jpeg'])
    
    prompt = st.text_area("Final Prompt", "Cinematic portrait of a fashion influencer, 8k, highly detailed.")
    
    generate_btn = st.button("Generate Influencer", type="primary", use_container_width=True)

with col2:
    st.subheader("Generation Status")
    
    if generate_btn:
        if not api_key:
            st.error("Please enter your API Key.")
        elif not all([pose_img, face_img, cloth_img]):
            st.warning("Please upload all three images.")
        else:
            api = NanoBananaAPI(api_key)
            try:
                # 1. Encoding
                with st.status("Encoding images...") as status:
                    p_b64 = api.encode_image(pose_img)
                    f_b64 = api.encode_image(face_img)
                    c_b64 = api.encode_image(cloth_img)
                    
                    # 2. Submit Task
                    status.update(label="Submitting task to Nano Banana...", state="running")
                    task_id = api.generate_image(prompt, p_b64, f_b64, c_b64)
                    st.write(f"Task ID created: `{task_id}`")
                    
                    # 3. Polling for results
                    status.update(label="Generating image (this may take 30-60s)...", state="running")
                    
                    placeholder = st.empty()
                    start_time = time.time()
                    max_wait = 300 # 5 minutes
                    
                    while time.time() - start_time < max_wait:
                        task_data = api.get_task_status(task_id)
                        success_flag = task_data.get('successFlag', 0)
                        
                        if success_flag == 1: # Success
                            status.update(label="Success!", state="complete")
                            img_url = task_data.get('response', {}).get('resultImageUrl')
                            if img_url:
                                st.image(img_url, caption="Generated AI Influencer")
                                st.balloons()
                            break
                        elif success_flag in [2, 3]: # Error
                            status.update(label="Generation Failed", state="error")
                            st.error(task_data.get('errorMessage', 'Unknown API Error'))
                            break
                        
                        # Wait 3 seconds before next poll
                        time.sleep(3)
                    else:
                        status.update(label="Timeout", state="error")
                        st.error("Generation timed out.")

            except Exception as e:
                st.error(f"Error: {str(e)}")
