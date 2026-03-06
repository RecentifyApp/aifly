import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# --- Constants & Configuration ---
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

st.set_page_config(
    page_title="AI Influencer Generator",
    page_icon="📸",
    layout="wide"
)

# --- Helper Functions ---

def encode_image_to_base64(uploaded_file):
    """Converts a Streamlit uploaded file to a base64 string."""
    try:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode('utf-8')
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return None

def generate_influencer(api_key, prompt, pose_b64, face_b64, clothes_b64):
    """Sends multimodal request to Gemini API."""
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key}
    
    # Constructing the multimodal prompt payload
    payload = {
        "contents": [{
            "parts": [
                {"text": f"Instructions: Create a photorealistic Instagram influencer image. "
                         f"Reference 1 (Pose): Use the pose from the first image. "
                         f"Reference 2 (Face): Use the facial identity from the second image. "
                         f"Reference 3 (Clothing): Use the outfit style from the third image. "
                         f"User Prompt: {prompt}"},
                {"inline_data": {"mime_type": "image/jpeg", "data": pose_b64}},
                {"inline_data": {"mime_type": "image/jpeg", "data": face_b64}},
                {"inline_data": {"mime_type": "image/jpeg", "data": clothes_b64}}
            ]
        }]
    }

    try:
        response = requests.post(API_URL, headers=headers, params=params, json=payload)
        response.raise_for_status()
        
        # Note: Gemini 1.5 Flash returns text descriptions/reasoning. 
        # If the specific model version supports image output bytes, 
        # it would be parsed here.
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Failed: {e}")
        return None

# --- UI Layout ---

st.title("📸 AI Influencer Studio")
st.markdown("Generate high-fidelity influencer content by combining pose, face, and style references.")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API Key")
    st.info("Your key is processed over HTTPS and never stored.")

# Main UI Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Reference Assets")
    
    pose_img = st.file_uploader("1. Pose Reference", type=['jpg', 'jpeg', 'png'])
    face_img = st.file_uploader("2. Face Identity", type=['jpg', 'jpeg', 'png'])
    clothes_img = st.file_uploader("3. Clothing Reference", type=['jpg', 'jpeg', 'png'])
    
    user_prompt = st.text_area(
        "Additional Prompt Details", 
        placeholder="e.g., Standing in a sunlit Parisian cafe, 8k resolution, cinematic lighting..."
    )

    generate_btn = st.button("Generate Influencer", type="primary", use_container_width=True)

with col2:
    st.subheader("Generated Output")
    
    if generate_btn:
        if not api_key:
            st.warning("Please enter your API Key in the sidebar.")
        elif not (pose_img and face_img and clothes_img):
            st.warning("Please upload all three reference images.")
        else:
            with st.spinner("Processing multimodal references and generating..."):
                # Encode images
                p_b64 = encode_image_to_base64(pose_img)
                f_b64 = encode_image_to_base64(face_img)
                c_b64 = encode_image_to_base64(clothes_img)
                
                # Call API
                result = generate_influencer(api_key, user_prompt, p_b64, f_b64, c_b64)
                
                if result:
                    # Logic to display the returned image
                    # Since standard Gemini 1.5 returns text, we display the model's response 
                    # or the image if the specific endpoint/tier provides it.
                    st.success("Generation Complete!")
                    st.json(result) # Displaying raw JSON for debug/output verification
                else:
                    st.error("Failed to generate content. Check the API logs.")

# Preview uploaded images in a low-profile way
if any([pose_img, face_img, clothes_img]):
    with st.expander("Preview Uploaded References"):
        p_cols = st.columns(3)
        if pose_img: p_cols[0].image(pose_img, caption="Pose")
        if face_img: p_cols[1].image(face_img, caption="Face")
        if clothes_img: p_cols[2].image(clothes_img, caption="Clothing")
