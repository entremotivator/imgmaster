# REQUIRED IMPORTS
import streamlit as st
import requests
import base64
import io
from PIL import Image

# Image conversion functions
def image_file_to_base64(uploaded_file):
    """Convert uploaded file to base64 using in-memory processing"""
    bytes_buffer = io.BytesIO()
    img = Image.open(uploaded_file).convert("RGB")
    img.save(bytes_buffer, format="JPEG")
    return base64.b64encode(bytes_buffer.getvalue()).decode('utf-8')

def image_url_to_base64(image_url):
    """Convert image URL to base64"""
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    return None

# Streamlit UI
st.title("Image to Video Generator")

# File uploader
uploaded_file = st.file_uploader("Upload image (JPEG/PNG)", 
                               type=["jpg", "jpeg", "png"])

# URL input
image_url = st.text_input("Or enter image URL:", 
                         value="https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg",
                         disabled=bool(uploaded_file))

# Image processing
image_b64 = None
if uploaded_file:
    try:
        st.image(uploaded_file, caption='Uploaded Image', 
                use_container_width=True)  # Fixed deprecation
        image_b64 = image_file_to_base64(uploaded_file)
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
elif image_url:
    try:
        st.image(image_url, caption='URL Image', 
                use_container_width=True)  # Fixed deprecation
        image_b64 = image_url_to_base64(image_url)
        if not image_b64:
            st.error("Failed to download image from URL")
    except Exception as e:
        st.error(f"URL image error: {str(e)}")

# API Configuration
api_key = st.text_input("API Key", value="YOUR_API_KEY")
prompt = st.text_area("Prompt", 
                     value="Kitten riding in an aeroplane and looking out the window.")
negative_prompt = st.text_area("Negative Prompt", 
                              value="No sudden movements, no fast zooms.")

# Generation logic
if st.button("Generate Video") and image_b64:
    if api_key == "YOUR_API_KEY":
        st.error("Please enter a valid API key")
    else:
        with st.spinner("Generating video..."):
            try:
                payload = {
                    "image": image_b64,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "cfg_scale": 0.5,
                    "mode": "pro",
                    "duration": 5
                }
                
                response = requests.post(
                    "https://api.segmind.com/v1/kling-image2video",
                    json=payload,
                    headers={'x-api-key': api_key},
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.success("Video generated successfully!")
                    st.download_button(
                        label="Download MP4",
                        data=response.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
