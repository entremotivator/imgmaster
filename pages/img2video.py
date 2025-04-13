import streamlit as st
import requests
from PIL import Image
import base64
import io
import re

# ---------- Background Removal Integration ----------
class BackgroundRemoval:
    def __init__(self, api_key):
        self.url = "https://api.segmind.com/v1/bg-removal"
        self.headers = {"x-api-key": api_key}

    def remove(self, image_url):
        payload = {"method": "object", "imageUrl": image_url}
        response = requests.post(self.url, json=payload, headers=self.headers)
        if response.status_code == 200:
            st.info(f"🧮 Remaining Credits: {response.headers.get('X-remaining-credits', 'N/A')}")
            return Image.open(io.BytesIO(response.content))
        else:
            raise Exception(f"Background removal failed: {response.status_code} - {response.text}")

# ---------- Base64 Helpers ----------
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

# ---------- URL Handling ----------
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
        if "image" not in response.headers.get("Content-Type", ""):
            raise ValueError("URL does not point to an image.")
        image = Image.open(io.BytesIO(response.content))
        return image_to_base64(image)
    except Exception as e:
        st.error(f"❌ Error fetching image from URL: {e}")
        return None

# ---------- UI Setup ----------
st.set_page_config(page_title="🖼️➡️🎥 Image to Video Generator", layout="centered")
st.title("🖼️➡️🎥 Image to Video Generator (w/ Optional BG Removal)")
st.markdown("Upload or paste a Dropbox/Google Drive link to convert an image to a **5-second video** using the Segmind Kling API.")

# ---------- Input Section ----------
st.header("📥 Upload Image")
uploaded_file = st.file_uploader("Upload JPG/PNG", type=["jpg", "jpeg", "png"])
image_url = st.text_input("Or paste an image URL", placeholder="Dropbox or Google Drive share link")
apply_bg_removal = st.checkbox("🧼 Remove background before generating video")

image_b64 = None
display_url = None
processed_image = None

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    processed_image = Image.open(uploaded_file)
elif image_url:
    direct_url = convert_to_direct_link(image_url)
    display_url = direct_url
    st.image(direct_url, caption="Image from URL", use_container_width=True)
    try:
        response = requests.get(direct_url)
        response.raise_for_status()
        processed_image = Image.open(io.BytesIO(response.content))
    except Exception as e:
        st.error(f"❌ Failed to load image from URL: {e}")

# ---------- Prompt & API ----------
st.divider()
st.header("⚙️ Prompt Settings")
api_key = st.text_input("🔐 API Key", type="password")
prompt = st.text_area("📝 Prompt", "A futuristic flying car over a cyberpunk city at night.")
negative_prompt = st.text_area("🚫 Negative Prompt", "Low resolution, distorted, blurry")

# ---------- Generate Video ----------
if st.button("🚀 Generate Video"):
    if not processed_image:
        st.error("❌ Please upload or link to an image first.")
    elif not api_key:
        st.error("❌ API key is required.")
    else:
        try:
            if apply_bg_removal:
                with st.spinner("Removing background..."):
                    remover = BackgroundRemoval(api_key)
                    processed_image = remover.remove(display_url if image_url else None)
                    st.image(processed_image, caption="Image after BG Removal", use_container_width=True)

            image_b64 = image_to_base64(processed_image)

            st.info("🔄 Generating 5-second video...")
            payload = {
                "image": image_b64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": 5
            }

            res = requests.post(
                "https://api.segmind.com/v1/kling-image2video",
                json=payload,
                headers={"x-api-key": api_key},
                timeout=600
            )

            if res.status_code == 200:
                st.success("✅ Video generated successfully!")
                st.video(io.BytesIO(res.content))
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
        st.code(image_b64[:300] + "...", language="text")
