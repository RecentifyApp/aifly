import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# --- Constants & Configuration ---
# Nano Banana 2 Model ID
MODEL_ID = "gemini-3.1-flash-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent"

st.set_page_config(
    page_title="AI Influencer Generator",
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

def generate_image(api_key, prompt, pose_b64, face_b64, clothes_b64):
    """Sends multimodal request to Nano Banana 2 API."""
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key}
    
    # We explicitly instruct Nano Banana to treat the inputs as specific references
    payload = {
        "contents": [{
            "parts": [
                {"text": (
                    "Using the following three images as references, generate a new high-quality image. "
                    "Image 1: Use strictly for the POSE and composition. "
                    "Image 2: Use strictly for the FACE identity and features. "
                    "Image 3: Use strictly for the CLOTHING and outfit style. "
                    f"Final Scene Description: {prompt}. "
                    "Output a photorealistic Instagram influencer photo."
                )},
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
        error_details = response.text if 'response' in locals() else str(e)
        st.error(f"API Error: {error_details}")
        return None

# --- UI Layout ---

st.title("📸 Nano Banana Influencer Studio")
st.markdown("Combine pose, face, and clothing into a single AI-generated influencer.")

with st.sidebar:
    st.header("Authentication")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    st.info(f"Model: {MODEL_ID}")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Reference Inputs")
    pose_img = st.file_uploader("1. Pose Reference", type=['jpg', 'png', 'jpeg'])
    face_img = st.file_uploader("2. Face Identity", type=['jpg', 'png', 'jpeg'])
    clothes_img = st.file_uploader("3. Clothing/Outfit", type=['jpg', 'png', 'jpeg'])
    
    user_prompt = st.text_area("Setting & Details", value="Standing in a futuristic neon city street at night, cinematic lighting.")
    
    generate_btn = st.button("Generate Influencer", type="primary", use_container_width=True)

with col2:
    st.subheader("Generated Result")
    
    if generate_btn:
        if not api_key:
            st.warning("Please enter your API Key.")
        elif not all([pose_img, face_img, clothes_img]):
            st.warning("Please upload all three reference images.")
        else:
            with st.spinner("Nano Banana is processing your images..."):
                p_b64 = encode_image_to_base64(pose_img)
                f_b64 = encode_image_to_base64(face_img)
                c_b64 = encode_image_to_base64(clothes_img)
                
                result = generate_image(api_key, user_prompt, p_b64, f_b64, c_b64)
                
                if result:
                    found_image = False
                    try:
                        # Parsing the response parts to find the image data
                        parts = result['candidates'][0]['content']['parts']
                        for part in parts:
                            if 'inline_data' in part:
                                img_data = base64.b64decode(part['inline_data']['data'])
                                gen_image = Image.open(BytesIO(img_data))
                                st.image(gen_image, caption="Generated AI Influencer", use_column_width=True)
                                
                                # Provide a download button
                                buf = BytesIO()
                                gen_image.save(buf, format="PNG")
                                st.download_button("Download Image", buf.getvalue(), "influencer.png", "image/png")
                                found_image = True
                                break
                        
                        if not found_image:
                            st.warning("The API returned text instead of an image. Try refining your prompt.")
                            if 'text' in parts[0]:
                                st.info(f"Model response: {parts[0]['text']}")
                                
                    except (KeyError, IndexError) as e:
                        st.error(f"Failed to parse image from response. JSON: {result}")

# Optional: Preview inputs
if any([pose_img, face_img, clothes_img]):
    with st.expander("View Uploaded References"):
        p_cols = st.columns(3)
        if pose_img: p_cols[0].image(pose_img, caption="Pose")
        if face_img: p_cols[1].image(face_img, caption="Face")
        if clothes_img: p_cols[2].image(clothes_img, caption="Clothing")
