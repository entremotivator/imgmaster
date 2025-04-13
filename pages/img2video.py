import streamlit as st
import requests
import base64
import io
from PIL import Image
import time
import warnings

# Suppress PIL warnings about palette images
warnings.filterwarnings('ignore', category=UserWarning, module='PIL.*')

# -----------------------------
# Image processing functions
# -----------------------------

def image_file_to_base64(uploaded_file):
    """Convert uploaded image to base64 with transparency handling"""
    try:
        img = Image.open(uploaded_file)

        # Handle palette and transparency
        if img.mode in ('P', 'PA'):
            img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')

        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        # Convert to JPEG in memory
        bytes_buffer = io.BytesIO()
        img.convert('RGB').save(bytes_buffer, format='JPEG', quality=95)
        return base64.b64encode(bytes_buffer.getvalue()).decode('utf-8')
    
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

def image_url_to_base64(image_url):
    """Convert image URL to base64, including Google Drive support"""
    try:
        # Google Drive direct link conversion
        if "drive.google.com" in image_url:
            if "file/d/" in image_url:
                file_id = image_url.split("/file/d/")[1].split("/")[0]
                image_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            elif "uc?id=" in image_url:
                pass  # already in correct format
            else:
                raise ValueError("Unsupported Google Drive URL format")

        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    
    except Exception as e:
        st.error(f"URL download error: {str(e)}")
        return None

# -----------------------------
# UI Configuration
# -----------------------------

st.set_page_config(page_title="Image to Video Generator", layout="centered")
st.title("🖼️➡️🎥 Image to Video Generator")
st.markdown("Convert your images into AI-generated videos using the Kling API.")

# -----------------------------
# Image Upload or URL Input
# -----------------------------

uploaded_file = st.file_uploader("Upload an image (JPEG/PNG)", 
                                 type=["jpg", "jpeg", "png"],
                                 help="Max size: 5MB")

image_url = st.text_input("Or enter an image URL (incl. Google Drive):", 
                          value="",
                          disabled=bool(uploaded_file),
                          help="Direct or shareable image link (JPEG/PNG)")

image_b64 = None

# Display image and process
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    image_b64 = image_file_to_base64(uploaded_file)
    if image_b64:
        st.success("✅ Image processed successfully.")
        st.code(f"Base64 size: {len(image_b64)//1000} KB", language="text")

elif image_url:
    st.image(image_url, caption="URL Image", use_container_width=True)
    image_b64 = image_url_to_base64(image_url)
    if image_b64:
        st.success("✅ URL image processed successfully.")
        st.code(f"Base64 size: {len(image_b64)//1000} KB", language="text")

# -----------------------------
# Generation Settings
# -----------------------------

st.divider()
st.subheader("🔧 Generation Settings")

api_key = st.text_input("API Key", value="YOUR_API_KEY", type="password")
prompt = st.text_area("Prompt", value="Kitten riding in an aeroplane and looking out the window.")
negative_prompt = st.text_area("Negative Prompt", value="No sudden movements, no fast zooms.")

# -----------------------------
# Generate Video
# -----------------------------

if st.button("🚀 Generate Video"):
    if not image_b64:
        st.error("❌ Please provide a valid image first.")
    elif api_key == "YOUR_API_KEY":
        st.error("❌ Please enter your actual API key.")
    else:
        with st.spinner("⏳ Generating video – please wait..."):
            payload = {
                "image": image_b64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": 5
            }

            max_retries = 3
            retry_delay = 10
            success = False

            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        "https://api.segmind.com/v1/kling-image2video",
                        json=payload,
                        headers={"x-api-key": api_key},
                        timeout=600
                    )

                    if response.status_code == 200:
                        st.success("🎉 Video generated successfully!")
                        st.download_button(
                            label="⬇️ Download MP4",
                            data=response.content,
                            file_name="generated_video.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                        success = True
                        break
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                        break

                except requests.Timeout:
                    st.warning(f"⏱️ Timeout on attempt {attempt+1}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                    break

            if not success:
                st.error("❌ Generation failed after multiple attempts.")

# -----------------------------
# Debug Info (Optional)
# -----------------------------

with st.expander("🛠️ Debug Info"):
    if image_b64:
        st.code(f"First 100 characters:\n{image_b64[:100]}...", language="text")
    st.write(f"Streamlit version: {st.__version__}")
    st.write(f"Pillow version: {Image.__version__}")

