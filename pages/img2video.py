import streamlit as st
import requests
from PIL import Image
import base64
import io
import re

# ---------- Image Base64 Handling ----------
def image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def uploaded_file_to_base64(uploaded_file) -> str:
    try:
        image = Image.open(uploaded_file)
        if image.mode in ('P', 'PA'):
            image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        return image_to_base64(image)
    except Exception as e:
        st.error(f"❌ Error processing uploaded file: {e}")
        return None

# ---------- URL Conversion ----------
def convert_to_direct_link(url: str) -> str:
    if "dropbox.com" in url:
        url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
    elif "drive.google.com" in url:
        match = re.search(r"/d/([^/]+)", url)
        if match:
            file_id = match.group(1)
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
        else:
            alt = re.search(r"id=([^&]+)", url)
            if alt:
                file_id = alt.group(1)
                url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

def fetch_image_base64_from_url(image_url: str) -> str:
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            raise ValueError("URL does not point to an image.")
        image = Image.open(io.BytesIO(response.content))
        return image_to_base64(image)
    except Exception as e:
        st.error(f"❌ Error fetching image from URL: {e}")
        return None

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Image to Video", layout="centered")
st.title("🖼️➡️🎥 Image to Video Generator (Enhanced Upload Handling)")
st.markdown("Upload an image or paste a Dropbox/Google Drive image link to generate a video using the Segmind Kling API.")

# File upload and URL input
uploaded_file = st.file_uploader("📤 Upload a JPG/PNG image", type=["jpg", "jpeg", "png"])
image_url = st.text_input("🌐 Or paste an image URL", placeholder="Dropbox or Google Drive share link")

image_b64 = None
display_url = None

# Handling uploaded file or URL input
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    image_b64 = uploaded_file_to_base64(uploaded_file)
elif image_url:
    direct_url = convert_to_direct_link(image_url)
    st.image(direct_url, caption="Image from URL", use_container_width=True)
    image_b64 = fetch_image_base64_from_url(direct_url)
    display_url = direct_url

# ---------- Prompt & API ----------
st.divider()
st.subheader("🎯 Prompt Settings")
api_key = st.text_input("🔐 API Key", type="password")
prompt = st.text_area("📝 Prompt", "A futuristic flying car over a cyberpunk city at night.")
negative_prompt = st.text_area("🚫 Negative Prompt", "Low resolution, distorted, blurry")

# Generate video on button click
if st.button("🚀 Generate Video"):
    if not image_b64:
        st.error("❌ Please upload an image or provide a valid image URL.")
    elif not api_key:
        st.error("❌ API key is required.")
    else:
        with st.spinner("Generating video..."):
            payload = {
                "image": image_b64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": 5  # video duration in seconds
            }
            try:
                res = requests.post(
                    "https://api.segmind.com/v1/kling-image2video",
                    json=payload,
                    headers={"x-api-key": api_key},
                    timeout=600
                )
                if res.status_code == 200:
                    st.success("✅ Video generated successfully!")
                    
                    # Show the video player in the app
                    video_path = io.BytesIO(res.content)
                    st.video(video_path, format="video/mp4")

                    # Provide download button for the video
                    st.download_button(
                        label="⬇️ Download MP4",
                        data=res.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error(f"❌ API Error: {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"❌ Exception: {e}")

# ---------- Debug Info ----------
with st.expander("🛠️ Debug Info"):
    if image_url:
        st.markdown(f"**Original URL:** `{image_url}`")
        st.markdown(f"**Direct Link:** `{display_url}`")
    if image_b64:
        # Show only the first 300 characters of the base64 string
        st.markdown("**Base64 Image Data (first 300 characters):**")
        st.code(image_b64[:300] + "...", language="text")
