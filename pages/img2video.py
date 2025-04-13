# REQUIRED IMPORTS
import streamlit as st
import requests
import base64
import io
from PIL import Image
import time
import warnings

# Suppress PIL warnings about palette images
warnings.filterwarnings('ignore', category=UserWarning, module='PIL.*')

# Image processing function with transparency handling
def image_file_to_base64(uploaded_file):
    """Convert uploaded image to base64 with proper transparency handling"""
    try:
        img = Image.open(uploaded_file)
        
        # Convert problematic image modes
        if img.mode in ('P', 'PA'):  # Palette-based images
            if 'transparency' in img.info:
                img = img.convert('RGBA')  # Preserve transparency
            else:
                img = img.convert('RGB')  # Fallback conversion
        
        # Handle alpha channel
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Apply alpha mask
            img = background
        
        # Convert to JPEG in memory
        bytes_buffer = io.BytesIO()
        img.convert('RGB').save(bytes_buffer, format='JPEG', quality=95)
        return base64.b64encode(bytes_buffer.getvalue()).decode('utf-8')
    
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

# URL image processing function
def image_url_to_base64(image_url):
    """Convert image URL to base64"""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        st.error(f"URL download error: {str(e)}")
        return None

# Streamlit UI Configuration
st.set_page_config(page_title="Image to Video Generator", layout="centered")
st.title("🖼️➡️🎥 Image to Video Generator")
st.markdown("Convert your images into AI-generated videos using the Kling API.")

# File uploader section
uploaded_file = st.file_uploader("Upload an image (JPEG/PNG)", 
                                 type=["jpg", "jpeg", "png"],
                                 help="Maximum size: 5MB")

# URL input section
image_url = st.text_input("Or enter an image URL:", 
                          value="https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg",
                          disabled=bool(uploaded_file),
                          help="Direct link to a JPEG or PNG image")

# Image display and processing
image_b64 = None
if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption='Uploaded Image', use_container_width=True)
    with col2:
        image_b64 = image_file_to_base64(uploaded_file)
        if image_b64:
            st.success("✅ Image processed successfully")
            st.code(f"Base64 length: {len(image_b64)//1000} KB", language="text")

elif image_url:
    try:
        st.image(image_url, caption='URL Image', use_container_width=True)
        image_b64 = image_url_to_base64(image_url)
        if image_b64:
            st.success("✅ URL image processed successfully")
            st.code(f"Base64 length: {len(image_b64)//1000} KB", language="text")
        else:
            st.error("⚠️ Failed to convert image from URL")
    except Exception as e:
        st.error(f"Image display error: {str(e)}")

# API Configuration Section
st.divider()
st.subheader("🔧 Generation Settings")
api_key = st.text_input("API Key", value="YOUR_API_KEY", type="password")
prompt = st.text_area("Prompt", 
                      value="Kitten riding in an aeroplane and looking out the window.",
                      height=100)
negative_prompt = st.text_area("Negative Prompt", 
                               value="No sudden movements, no fast zooms.",
                               height=100)

# Generation button with retry logic
if st.button("🚀 Generate Video"):
    if not image_b64:
        st.error("❌ Please provide a valid image first.")
    elif api_key == "YOUR_API_KEY":
        st.error("❌ Please enter a valid API key.")
    else:
        with st.spinner("⏳ Generating video – this may take several minutes..."):
            payload = {
                "image": image_b64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5,
                "mode": "pro",
                "duration": 5
            }

            max_retries = 3
            retry_delay = 10  # seconds
            success = False

            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        "https://api.segmind.com/v1/kling-image2video",
                        json=payload,
                        headers={'x-api-key': api_key},
                        timeout=600  # 10-minute timeout
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
                    st.warning(f"⏱️ Attempt {attempt+1} timed out. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

                except Exception as e:
                    st.error(f"Unexpected error during generation: {str(e)}")
                    break

            if not success:
                st.error("❌ Video generation failed after multiple attempts. Please try again.")

# Debug section (optional)
with st.expander("🛠️ Debug Info"):
    if image_b64:
        st.code(f"First 100 characters of base64:\n{image_b64[:100]}...", language="text")
    st.write(f"Streamlit version: {st.__version__}")
    st.write(f"Pillow version: {Image.__version__}")
