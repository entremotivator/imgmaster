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
        st.error(f"Failed to fetch image from URL: {e}")
        return None

# User selects input method
input_method = st.radio("Choose image input method:", ["Upload Image", "Image URL"])

# Variables for image and prompt
base64_image = None
prompt = ""
image_source = ""

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
    duration = st.slider("Video Duration (seconds)", min_value=2, max_value=10, value=5)
    submitted = st.form_submit_button("Generate Video")

# Main logic after submission
if submitted:
    if not api_key:
        st.warning("Please enter your API key in the sidebar to continue.")
    else:
        if input_method == "Upload Image":
            if not uploaded_file:
                st.error("Please upload an image file.")
            else:
                base64_image = image_file_to_base64(uploaded_file)
                image_source = "upload"
        else:
            base64_image = image_url_to_base64(image_url)
            image_source = "url"

        if base64_image:
            st.info(f"Using image from: {image_source}")

            url = "https://api.segmind.com/v1/kling-image2video"
            data = {
                "image": base64_image,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": duration
            }

            headers = {'x-api-key': api_key}

            with st.spinner("🚀 Generating video..."):
                try:
                    response = requests.post(url, json=data, headers=headers)
                    response.raise_for_status()
                    st.success("✅ Video generated successfully!")
                    st.code(response.content.decode())
                    # If you expect a URL or binary response, handle accordingly here
                except Exception as e:
                    st.error(f"❌ Generation failed: {e}")
