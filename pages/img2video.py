import streamlit as st
import requests
import base64
import io
from PIL import Image
import re
import warnings

# Suppress image warnings
warnings.filterwarnings("ignore", category=UserWarning, module='PIL.*')

# Convert uploaded file to base64
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
        st.error(f"Error processing uploaded image: {e}")
        return None

# Convert Dropbox or Google Drive URL to direct link
def convert_to_direct_link(url):
    if "dropbox.com" in url:
        # Convert Dropbox to direct link
        if "?dl=0" in url:
            url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
        elif "?dl=1" not in url:
            url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com") + "?dl=1"
    elif "drive.google.com" in url:
        # Convert Google Drive share link to direct download link
        match = re.search(r"/d/([^/]+)", url)
        if match:
            file_id = match.group(1)
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
        else:
            match_alt = re.search(r"id=([^&]+)", url)
            if match_alt:
                file_id = match_alt.group(1)
                url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

# Fetch image from URL and convert to base64
def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            raise ValueError("URL does not point to a valid image.")
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        st.error(f"Error downloading image from URL: {e}")
        return None

# Streamlit UI
st.set_page_config(page_title="Image to Video Generator", layout="centered")
st.title("🖼️➡️🎥 Generate Video from Image")
st.markdown("Upload an image or paste an image URL (Dropbox & Google Drive supported) to create a video using the Segmind Kling API.")

# Upload or URL input
uploaded_file = st.file_uploader("📤 Upload a JPG/PNG image", type=["jpg", "jpeg", "png"])
image_url = st.text_input(
    "🌐 Or paste a direct image URL (Dropbox / Google Drive supported)",
    placeholder="https://drive.google.com/file/d/FILE_ID/view?usp=sharing",
    help="URL must point directly to an image (.jpg/.jpeg/.png). For Dropbox, make sure it ends with '?dl=0'."
)

image_b64 = None
image_preview_url = None

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    image_b64 = image_file_to_base64(uploaded_file)
elif image_url:
    direct_url = convert_to_direct_link(image_url)
    st.image(direct_url, caption="Image from URL", use_container_width=True)
    image_b64 = image_url_to_base64(direct_url)
    image_preview_url = direct_url

# Prompt fields
st.divider()
st.subheader("🎯 Prompt Settings")
api_key = st.text_input("🔐 API Key", type="password")
prompt = st.text_area("📝 Prompt", "A futuristic flying car over a cyberpunk city at night.")
negative_prompt = st.text_area("🚫 Negative Prompt", "Low resolution, distorted, blurry")

# Submit button
if st.button("🚀 Generate Video"):
    if not image_b64:
        st.error("❌ Please provide a valid image first.")
    elif not api_key or api_key == "YOUR_API_KEY":
        st.error("❌ Please enter a valid API key.")
    else:
        with st.spinner("Processing image and generating video..."):
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
                    st.success("✅ Video generated successfully!")
                    st.download_button(
                        label="⬇️ Download Video",
                        data=response.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error(f"❌ API returned an error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"❌ Failed to generate video: {str(e)}")

# Debug info
with st.expander("🧪 Debug Info"):
    if image_url:
        st.markdown(f"**Original URL:** `{image_url}`")
        st.markdown(f"**Processed Direct Link:** `{image_preview_url}`")
    if image_b64:
        st.code(image_b64[:200] + "...", language="text")
