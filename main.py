from utils.upload_garment import upload_garment
from utils.upload_user_image import upload_user_image
from utils.api import get_result, pil_to_b64
import concurrent.futures
from streamlit_image_select import image_select
import streamlit as st
import time
from functools import partial

st.set_page_config(layout="wide")


def main():
    user_col, garment_col, result_col = st.columns(3)
    with user_col:
        user_images = upload_user_image()
        process_user_image = st.toggle("Process user image", value=True)
        process_garment_image = st.toggle("Process garment images", value=True)
        use_auto_prompting = st.toggle("Use auto prompting", value=True)
        use_refiner = st.toggle("Use refiner", value=True)
        if user_images:
            user_image = image_select(
                "Select a user image", user_images, use_container_width=False
            )
            if user_image:
                st.image(
                    user_image, caption="Selected User Image", use_column_width=True
                )

    with garment_col:
        garment_images: list = upload_garment()
        submit_btn = st.button("Submit")
        body_parts = [
            "full_body",
            "dresses",
            "upper_clothes",
            "lower_body_skirts",
            "lower_body_pants",
        ]

        if garment_images:
            garment_image_index = image_select(
                "Select a garment",
                garment_images,
                use_container_width=False,
                return_value="index",
            )
            if garment_image_index is not None:
                st.image(
                    garment_images[garment_image_index],
                    caption="Selected Garment Image",
                    use_column_width=True,
                )
                if "garment_state" not in st.session_state:
                    st.session_state.garment_state = {}
                garment_dict = st.session_state.garment_state or {}
                this_garment_info = garment_dict.get(garment_image_index, {})

                selected_body_part = this_garment_info.get("body_part", body_parts[0])
                selected_description = this_garment_info.get("description", "")

                body_part = st.selectbox(
                    "Select a body part",
                    body_parts,
                    index=body_parts.index(selected_body_part),
                )
                description = st.text_input("Description", value=selected_description)
                this_garment_info = {
                    "image": garment_images[garment_image_index],
                    "description": description,
                    "body_part": body_part,
                }
                print(st.session_state.garment_state)
                save_btn = st.button("Save")
                if save_btn:
                    garment_dict[garment_image_index] = this_garment_info
                    st.session_state.garment_state = garment_dict
                    print(st.session_state.garment_state)
                    st.write("Saved for garment", garment_image_index)
    with result_col:
        st.header("Output")
        output_image_holder = st.empty()
        status_holder = st.empty()

        if submit_btn:
            start_time = time.time()
            with status_holder.status(
                f"Processing: {time.time() - start_time}s"
            ) as status:
                params = {
                    "process_user_image": process_user_image,
                    "process_garment_image": process_garment_image,
                    "use_auto_prompting": use_auto_prompting,
                    "use_refiner": use_refiner,
                }
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    t = executor.submit(
                        get_result, user_image, st.session_state.garment_state, params
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
