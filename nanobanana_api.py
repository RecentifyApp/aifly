import streamlit as st
import requests
from PIL import Image
from io import BytesIO

API_KEY = st.secrets["NANOBANANA_API_KEY"]

def generate_image(pose, face, clothes, prompt):

    url = "https://api.nanobanana.ai/generate"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    files = {}

    if pose:
        files["pose"] = ("pose.png", pose, "image/png")

    if face:
        files["face"] = ("face.png", face, "image/png")

    if clothes:
        files["clothes"] = ("clothes.png", clothes, "image/png")

    data = {
        "prompt": prompt
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data
    )

    result = response.json()

    image_url = result["image_url"]

    img_response = requests.get(image_url)

    return Image.open(BytesIO(img_response.content))
