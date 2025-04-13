import streamlit as st
import requests
import base64
import io
from PIL import Image
import time
import warnings

# Suppress image warnings
warnings.filterwarnings('ignore', category=UserWarning, module='PIL.*')

# Convert uploaded image file to base64
def image_file_to_base64(uploaded_file):
    try:
        img = Image.open(uploaded_file)

        if img.mode in ('P', 'PA'):
            img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')

        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# Convert image URL to base64
def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

# Convert Dropbox link to direct link
def convert_dropbox_url(url):
    if "dropbox.com" in url and "?dl=0" in url:
        return url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
    return url

# App layout
st.set_page_config(page_title="Image to Video Generator", layout="centered")
st.title("🖼️➡️🎥 Image to Video Generator")
st.markdown("Upload an image or paste an image URL (Dropbox supported) to generate a video using the Kling API.")

# Image input
uploaded_file = st.file_uploader("Upload a JPG/PNG image", type=["jpg", "jpeg", "png"])
image_url = st.text_input(
    "Or paste a direct image URL (Dropbox supported)",
    placeholder="https://www.dropbox.com/s/xxxxxxx/sample.jpg?dl=0",
    help="Must be a direct link to a .jpg/.jpeg/.png image. Dropbox links should end with '?dl=0'"
)

# Image preview and conversion
image_b64 = None
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    image_b64 = image_file_to_base64(uploaded_file)
elif image_url:
    clean_url = convert_dropbox_url(image_url)
    st.image(clean_url, caption="Image from URL", use_container_width=True)
    image_b64 = image_url_to_base64(clean_url)

# Prompt input
st.divider()
st.subheader("🎯 Prompt Settings")
api_key = st.text_input("🔐 API Key", type="password")
prompt = st.text_area("📝 Prompt", "A cat floating in space with stars around.")
negative_prompt = st.text_area("🚫 Negative Prompt", "No low quality, no artifacts.")

# Submit button
if st.button("🚀 Generate Video"):
    if not image_b64:
        st.error("❌ Please provide an image.")
    elif not api_key or api_key == "YOUR_API_KEY":
        st.error("❌ Please enter a valid API key.")
    else:
        with st.spinner("Generating video... this may take a few minutes"):
            payload = {
                "image": image_b64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": 5
            }

            try:
                response = requests.post(
                    "https://api.segmind.com/v1/kling-image2video",
                    json=payload,
                    headers={"x-api-key": api_key},
                    timeout=600
                )

                if response.status_code == 200:
                    st.success("🎉 Video generated!")
                    st.download_button(
                        label="⬇️ Download Video",
                        data=response.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error(f"❌ API Error {response.status_code}: {response.text}")

            except requests.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

# Debug Info
with st.expander("🛠️ Debug Info"):
    if image_b64:
        st.code(image_b64[:100] + "...", language="text")
    st.write("Streamlit version:", st.__version__)
    st.write("Pillow version:", Image.__version__)

