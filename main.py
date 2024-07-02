from utils.upload_garment import upload_garment
from utils.upload_user_image import upload_user_image
from utils.api import get_result
import concurrent.futures
from streamlit_image_select import image_select
import streamlit as st
import time


def main():
    user_col, garment_col, result_col = st.columns(3)
    with user_col:
        user_images = upload_user_image()
        if user_images:
            user_image = image_select(
                "Select a user image", user_images, use_container_width=False
            )
        if user_image:
            st.image(user_image, caption="Selected User Image", use_column_width=True)

    with garment_col:
        garment_images: dict = upload_garment()
        submit_btn = st.button("Submit")
        body_parts = [
            "full_body",
            "dresses",
            "upper_clothes",
            "lower_body_skirts",
            "lower_body_pants",
        ]
        body_part = st.selectbox("Select a body part", body_parts)
        if garment_images:
            garment_image = image_select(
                "Select a garment", garment_images, use_container_width=False
            )
        if garment_image:
            st.image(
                garment_image, caption="Selected Garment Image", use_column_width=True
            )

    with result_col:
        st.header("Output")
        output_image_holder = st.empty()
        status_holder = st.empty()

        if submit_btn:
            st.image(user_image, caption="User Image", use_column_width=True)
            st.image(garment_image, caption="Garment Image", use_column_width=True)
            start_time = time.time()
            with status_holder.status(
                f"Processing: {time.time() - start_time}s"
            ) as status:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    t = executor.submit(
                        get_result, user_image, garment_image, None, body_part
                    )
                    while not t.done():
                        elapsed_time = round(time.time() - start_time, 2)
                        status.update(
                            label=f"Processing: {elapsed_time}s", state="running"
                        )
                        time.sleep(0.1)
                        if t.done():
                            status.update(
                                label=f"Completed: {elapsed_time}s", state="complete"
                            )
                output_image, mask_image, executionTime = t.result()
                status.success("Done!")
            if output_image:
                output_image_holder.image(output_image, use_column_width=True)


if __name__ == "__main__":
    main()
