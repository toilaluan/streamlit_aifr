import streamlit as st
from PIL import Image
import io


def upload_garment():
    images = st.file_uploader(
        "Upload garments",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="garment_images",
    )
    images = [Image.open(io.BytesIO(image.read())).convert("RGB") for image in images]
    return images
