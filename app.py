import streamlit as st
import requests
import base64
import json

# --- Constants & Configuration ---
# Updated to the latest stable model ID
MODEL_ID = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent"

st.set_page_config(
    page_title="AI Influencer Studio",
    page_icon="📸",
    layout="wide"
)

# --- Helper Functions ---

def encode_image_to_base64(uploaded_file):
    """Converts a Streamlit uploaded file to a base64 string."""
    try:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return None

def generate_influencer_content(api_key, prompt, pose_b64, face_b64, clothes_b64):
    """Sends multimodal request to the updated Gemini 2.5 API."""
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key}
    
    # Structured prompt to guide the model's multimodal reasoning
    full_prompt = (
        "ACT AS A PHOTOREALISTIC IMAGE GENERATOR ENGINE. "
        "Analysis Tasks:\n"
        "1. Extract the exact physical pose from Image 1.\n"
        "2. Extract the facial features and identity from Image 2.\n"
        "3. Extract the clothing style and textures from Image 3.\n\n"
        f"USER SPECIFICATIONS: {prompt}\n\n"
        "OUTPUT REQUIREMENT: Generate a highly detailed, cinematic Instagram influencer image "
        "merging these three references perfectly."
    )

    payload = {
        "contents": [{
            "parts": [
                {"text": full_prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": pose_b64}},
                {"inline_data": {"mime_type": "image/jpeg", "data": face_b64}},
                {"inline_data": {"mime_type": "image/jpeg", "data": clothes_b64}}
            ]
        }]
    }

    try:
        response = requests.post(API_URL, headers=headers, params=params, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Provide more context on the error for the user
        error_msg = response.text if 'response' in locals() else str(e)
        st.error(f"API Error: {error_msg}")
        return None

# --- UI Layout ---

st.title("📸 AI Influencer Studio v2.5")
st.markdown("Utilizing **Gemini 2.5 Flash** for high-fidelity multimodal synthesis.")

with st.sidebar:
    st.header("Authentication")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.info(f"Currently using model: {MODEL_ID}")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Reference Assets")
    pose_img = st.file_uploader("1. Pose Reference (Image 1)", type=['jpg', 'jpeg', 'png'])
    face_img = st.file_uploader("2. Face Identity (Image 2)", type=['jpg', 'jpeg', 'png'])
    clothes_img = st.file_uploader("3. Clothing Reference (Image 3)", type=['jpg', 'jpeg', 'png'])
    
    user_prompt = st.text_area("Scene Description", value="Standing in a luxury penthouse at sunset, hyper-realistic, 8k.")
    
    if st.button("Generate Influencer", type="primary", use_container_width=True):
        if not api_key:
            st.warning("Please provide an API Key.")
        elif not all([pose_img, face_img, clothes_img]):
            st.warning("All three reference images are required.")
        else:
            with st.spinner("Analyzing references and generating..."):
                p_b64 = encode_image_to_base64(pose_img)
                f_b64 = encode_image_to_base64(face_img)
                c_b64 = encode_image_to_base64(clothes_img)
                
                result = generate_influencer_content(api_key, user_prompt, p_b64, f_b64, c_b64)
                
                if result:
                    st.session_state['api_result'] = result

with col2:
    st.subheader("Generation Result")
    if 'api_result' in st.session_state:
        # Note: In standard Gemini API, image generation returns are often 
        # handled via specific media parts or specialized Nano Banana endpoints.
        # This displays the response content.
        res = st.session_state['api_result']
        try:
            # Attempting to extract text or media from the standard response format
            text_response = res['candidates'][0]['content']['parts'][0]['text']
            st.write(text_response)
        except (KeyError, IndexError):
            st.json(res)
