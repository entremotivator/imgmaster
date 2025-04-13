import streamlit as st
import requests
import base64
from PIL import Image
import io

# Sidebar for API key
st.sidebar.title("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your API Key", type="password")

st.title("🎬 Kling Image-to-Video Generator")

# Helper functions
def image_file_to_base64(uploaded_file):
    """Convert uploaded image file to base64."""
    image = Image.open(uploaded_file)
    buffer = io.BytesIO()
    save_format = image.format or "PNG"
    image.save(buffer, format=save_format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def image_url_to_base64(image_url):
    """Fetch image from URL and convert to base64."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        st.error(f"❌ Failed to fetch image from URL: {e}")
        return None

# Input method
input_method = st.radio("Choose image input method:", ["Upload Image", "Image URL"])

# Form inputs
with st.form("kling_form"):
    uploaded_file = None
    image_url = None

    if input_method == "Upload Image":
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            st.image(Image.open(uploaded_file), caption="Uploaded Image", use_container_width=True)
    else:
        image_url = st.text_input("Image URL", "https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg")

    prompt = st.text_input("Prompt", "Kitten riding in an aeroplane and looking out the window.")
    negative_prompt = st.text_input("Negative Prompt", "No sudden movements, no fast zooms.")
    duration = st.slider("Video Duration (seconds)", min_value=5, max_value=10, value=5, step=5)
    version = st.selectbox("Kling Version", ["1.6", "1.5"])
    submitted = st.form_submit_button("Generate Video")

# Process submission
if submitted:
    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar.")
    else:
        base64_image = None

        if input_method == "Upload Image":
            if uploaded_file:
                base64_image = image_file_to_base64(uploaded_file)
            else:
                st.error("❌ Please upload an image.")
        else:
            base64_image = image_url_to_base64(image_url)

        if base64_image:
            url = "https://api.segmind.com/v1/kling-image2video"
            payload = {
                "image": base64_image,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": duration,
                "version": version
            }
            headers = {"x-api-key": api_key}

            with st.spinner("🚀 Generating video..."):
                try:
                    response = requests.post(url, json=payload, headers=headers)
                    if response.status_code == 401:
                        error_msg = response.json().get("error", "Unauthorized access.")
                        st.error(f"❌ Error: {error_msg}")
                    elif response.status_code != 200:
                        st.error(f"❌ Request failed: {response.status_code}")
                        st.text(response.content.decode())
                    else:
                        video_data = response.json()
                        video_url = video_data.get("video_url")
                        if video_url:
                            st.success("✅ Video generated successfully!")
                            st.video(video_url)
                        else:
                            st.error("❌ Video URL not found in response.")
                except Exception as e:
                    st.exception(f"❌ Unexpected error: {e}")
