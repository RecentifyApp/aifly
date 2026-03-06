import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuration ---
# Based on Nano Banana API documentation
API_ENDPOINT = "https://api.nanobanana.ai/v1/generate"

st.set_page_config(
    page_title="Nano Banana Influencer Studio",
    page_icon="🍌",
    layout="wide"
)

# --- Helper Functions ---

def encode_image_to_base64(uploaded_file):
    """Encodes uploaded file to base64 string for the Nano Banana API."""
    if uploaded_file is None:
        return None
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def generate_influencer_image(api_key, prompt, pose_b64, face_b64, cloth_b64):
    """
    Sends the 3-image multimodal request to Nano Banana.
    Nano Banana 2 (Gemini 3 Flash Image) supports image-to-image composition.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Constructing the payload per Nano Banana's multimodal composition spec
    payload = {
        "model": "nano-banana-2",
        "prompt": prompt,
        "images": [
            {"data": pose_b64, "type": "pose_reference"},
            {"data": face_b64, "type": "face_identity"},
            {"data": cloth_b64, "type": "clothing_reference"}
        ],
        "parameters": {
            "resolution": "1080x1350", # Standard Instagram Portrait
            "guidance_scale": 7.5,
            "realism_mode": True
        }
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Nano Banana API Error: {e}")
        if response.text:
            st.code(response.text)
        return None

# --- UI Layout ---

st.title("🍌 Nano Banana Influencer Studio")
st.info("Senior Engineer Note: This app uses the Nano Banana 2 multimodal engine to blend pose, face, and style.")

with st.sidebar:
    st.header("API Credentials")
    api_key = st.text_input("Nano Banana API Key", type="password", help="Get your key at nanobananaapi.ai")
    st.divider()
    st.write("### Model Settings")
    resolution = st.selectbox("Resolution", ["1080x1350", "1024x1024", "720x1280"])

# Main Application Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Reference Assets")
    
    pose_file = st.file_uploader("1. Upload Pose Reference", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. Upload Influencer Face", type=['png', 'jpg', 'jpeg'])
    cloth_file = st.file_uploader("3. Upload Clothing/Style", type=['png', 'jpg', 'jpeg'])
    
    custom_prompt = st.text_area(
        "Scene Description", 
        value="A high-end fashion influencer walking down a street in Milan, soft morning sunlight, 8k photorealistic.",
        height=100
    )

    generate_btn = st.button("Generate Influencer", type="primary", use_container_width=True)

with col2:
    st.subheader("Generated Output")
    
    if generate_btn:
        if not api_key:
            st.error("Please provide your Nano Banana API key in the sidebar.")
        elif not all([pose_file, face_file, cloth_file]):
            st.warning("All three reference images are required for this model.")
        else:
            with st.spinner("Banana is peeling the data... generating your influencer..."):
                # Encode images
                p_b64 = encode_image_to_base64(pose_file)
                f_b64 = encode_image_to_base64(face_file)
                c_b64 = encode_image_to_base64(cloth_file)
                
                # Call API
                result = generate_influencer_image(api_key, custom_prompt, p_b64, f_b64, c_b64)
                
                if result and "image_url" in result:
                    st.image(result["image_url"], caption="Final AI Influencer Output")
                    st.success("Generation Successful!")
                    
                    # Download option
                    img_res = requests.get(result["image_url"])
                    st.download_button("Download High-Res", img_res.content, "influencer.png", "image/png")
                
                elif result and "b64_json" in result:
                    # If API returns base64 directly
                    img_bytes = base64.b64decode(result["b64_json"])
                    st.image(img_bytes, caption="Final AI Influencer Output")
                    st.success("Generation Successful!")
                else:
                    st.error("Model failed to return an image. Check prompt constraints.")

# Reference Previews
if any([pose_file, face_file, cloth_file]):
    with st.expander("Preview Selected Assets"):
        p_cols = st.columns(3)
        if pose_file: p_cols[0].image(pose_file, caption="Pose")
        if face_file: p_cols[1].image(face_file, caption="Face")
        if cloth_file: p_cols[2].image(cloth_file, caption="Clothing")
