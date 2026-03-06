import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

API_KEY = st.secrets["NANOBANANA_API_KEY"]

def encode_image(file):
    if file is None:
        return None
    return base64.b64encode(file.read()).decode("utf-8")


def generate_image(pose, face, clothes, prompt):

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY
    }

    parts = [{"text": prompt}]

    pose_b64 = encode_image(pose)
    face_b64 = encode_image(face)
    clothes_b64 = encode_image(clothes)

    if pose_b64:
        parts.append({
            "inline_data":{
                "mime_type":"image/png",
                "data":pose_b64
            }
        })

    if face_b64:
        parts.append({
            "inline_data":{
                "mime_type":"image/png",
                "data":face_b64
            }
        })

    if clothes_b64:
        parts.append({
            "inline_data":{
                "mime_type":"image/png",
                "data":clothes_b64
            }
        })

    data = {
        "contents":[
            {
                "parts":parts
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    result = response.json()

    try:

        parts = result["candidates"][0]["content"]["parts"]

        for part in parts:

            if "inline_data" in part:

                image_data = part["inline_data"]["data"]

                image_bytes = base64.b64decode(image_data)

                return Image.open(BytesIO(image_bytes))

    except:
        st.error(result)
        return None
