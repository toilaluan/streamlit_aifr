import streamlit as st
from PIL import Image
import io


def upload_user_image():
    images = st.file_uploader(
        "Upload garments",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="user_images",
    )
    images = [Image.open(io.BytesIO(image.read())).convert("RGB") for image in images]
    return images
