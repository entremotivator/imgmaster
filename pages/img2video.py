import streamlit as st
import requests
import base64
from PIL import Image
import io

# Sidebar for API key
st.sidebar.title("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your API Key", type="password")

st.title("🎬 Kling Image-to-Video Generator")

# Helpers
def image_file_to_base64(uploaded_file):
    image = Image.open(uploaded_file)
    buffer = io.BytesIO()
    save_format = image.format if image.format else "PNG"
    image.save(buffer, format=save_format)
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')

def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        st.error(f"❌ Failed to fetch image from URL: {e}")
        return None

# User selects input method
input_method = st.radio("Choose image input method:", ["Upload Image", "Image URL"])

# Form for user inputs
with st.form("kling_form"):
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            st.image(Image.open(uploaded_file), caption="Uploaded Image", use_column_width=True)
    else:
        image_url = st.text_input("Image URL", "https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg")

    prompt = st.text_input("Prompt", "Kitten riding in an aeroplane and looking out the window.")
    negative_prompt = st.text_input("Negative Prompt", "No sudden movements, no fast zooms.")
    duration = st.slider("Video Duration (seconds)", min_value=5, max_value=10, value=5, step=5)
    version = st.selectbox("Kling Version", ["1.6", "1.5"])
    submitted = st.form_submit_button("Generate Video")

# Main logic after submission
if submitted:
    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar to continue.")
    else:
        base64_image = None
        if input_method == "Upload Image":
            if not uploaded_file:
                st.error("❌ Please upload an image file.")
            else:
                base64_image = image_file_to_base64(uploaded_file)
        else:
            base64_image = image_url_to_base64(image_url)

        if base64_image:
            url = "https://api.segmind.com/v1/kling-image2video"
            payload = {
                "image": base64_image,  # REQUIRED
                "prompt": prompt,  # REQUIRED
                "negative_prompt": negative_prompt,  # Optional but recommended
                "cfg_scale": 0.5,  # Must be float between 0-1
                "mode": "pro",  # Only "pro" or "std"
                "duration": duration,  # Only 5 or 10
                "version": version  # REQUIRED for Kling 1.6
            }

            headers = {'x-api-key': api_key}

            with st.spinner("🚀 Generating video..."):
                try:
                    response = requests.post(url, json=payload, headers=headers)

                    if response.status_code == 401:
                        error_msg = response.json().get("error", "Unauthorized access.")
                        st.error(f"❌ Error: {error_msg}")
                    elif response.status_code != 200:
                        st.error(f"❌ Request failed with status {response.status_code}")
                        st.text(response.content.decode())
                    else:
                        st.success("✅ Video generated successfully!")
                        st.code(response.content.decode())  # Replace with actual display logic if needed

                except Exception as e:
                    st.exception(f"❌ Unexpected error: {e}")
