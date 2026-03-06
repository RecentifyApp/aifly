import streamlit as st
from nanobanana_api import generate_image
from prompt_builder import build_prompt

st.set_page_config(page_title="AI Influencer Generator", layout="wide")

st.title("AI Influencer Generator")

st.write("Create AI influencers using pose, face, and clothing references.")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Upload Images")

    pose_image = st.file_uploader(
        "Pose Reference Image",
        type=["png","jpg","jpeg"]
    )

    face_image = st.file_uploader(
        "Influencer Face Image",
        type=["png","jpg","jpeg"]
    )

    clothes_image = st.file_uploader(
        "Clothing Reference",
        type=["png","jpg","jpeg"]
    )

with col2:

    st.subheader("Scene Settings")

    location = st.selectbox(
        "Location",
        ["Beach","Gym","Coffee shop","Luxury hotel","Street"]
    )

    camera = st.selectbox(
        "Camera Style",
        ["iPhone","DSLR","Mirror","Studio"]
    )

    base_prompt = st.text_area(
        "Base Prompt",
        "beautiful instagram influencer woman"
    )

st.divider()

generate_button = st.button("Generate Influencer")

if generate_button:

    if not face_image:
        st.error("Please upload at least a face image.")
        st.stop()

    prompt = build_prompt(base_prompt, location, camera)

    with st.spinner("Generating image..."):

        try:

            image = generate_image(
                pose_image,
                face_image,
                clothes_image,
                prompt
            )

            st.success("Image generated!")

            st.image(image, use_column_width=True)

        except Exception as e:
            st.error(str(e))
