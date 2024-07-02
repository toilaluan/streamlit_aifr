import io
import runpod
import json
import os
import requests
import time
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
import hmac

# load runpod api key and serverless model id
runpod.api_key = os.environ.get("RUNPOD_API_KEY")  # get evironment variable
RUNPOD_MODEL_ID = os.environ.get("RUNPOD_MODEL_ID")

# endpoint = runpod.Endpoint(RUNPOD_MODEL_ID)


def get_result(
    user_image, clothes_image, mask_image_upload=None, body_part="upper_body"
):

    input = {
        "human_img_b64": pil_to_b64(user_image),
        "garm_img_b64": pil_to_b64(clothes_image),
        "mask_img": pil_to_b64(mask_image_upload) if mask_image_upload else None,
        "body_part": body_part,
        "is_checked_crop": True,
    }

    start = time.time()

    # First way to call serverless api
    # run_request = endpoint.run_sync(input)

    # Second way to call serverless api
    url = f"https://api.runpod.ai/v2/{RUNPOD_MODEL_ID}/runsync"  # or change to runsync
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {runpod.api_key}",
    }
    run_request = requests.post(url, headers=headers, data=json.dumps({"input": input}))
    print("run_request:", run_request)
    run_request = run_request.json()
    with open("run_request.json", "w") as f:
        json.dump(run_request, f)
    executionTime = run_request["executionTime"] / 1000
    print("Execution time: ", executionTime)
    # save run_request to json file

    run_request = run_request["output"]
    end = time.time()
    my_request_time = end - start
    print("Send request and receive responce taken: ", my_request_time)
    my_request_time = round(my_request_time, 2)
    start = time.time()
    output_image_b64 = run_request["output_image"]
    output_image = b64_to_pil(output_image_b64)

    mask_image_b64 = run_request["mask_image"]
    mask_image = b64_to_pil(mask_image_b64)
    end = time.time()
    convert_b64_to_pil_time = end - start
    print("Convert b64 to pil takes: ", convert_b64_to_pil_time)

    return output_image, mask_image, executionTime


def b64_to_pil(base64_string):
    # Decode the base64 string
    image_data = base64.b64decode(base64_string)

    # Create a PIL Image object from the decoded image data
    image = Image.open(BytesIO(image_data))
    return image


def pil_to_b64(pil_img):
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def resize_img_to768(img):
    aspect_ratio = img.height / img.width
    new_width = 768
    new_height = int(new_width * aspect_ratio)

    # Resize the image
    img_resized = img.resize((new_width, new_height))
    return img_resized


def convert_to_jpg(img):
    # Convert image to RGB if it is not
    if img.mode != "RGB":
        img = img.convert("RGB")
        # Create a BytesIO object to hold the JPEG data
        jpeg_image_io = io.BytesIO()

        # Save the image to the BytesIO object as JPEG
        img.save(jpeg_image_io, "JPEG")
    return img


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False
