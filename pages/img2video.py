import streamlit as st
import requests
import base64
from PIL import Image
import io
import tempfile
import os
import time
import uuid
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Kling Image-to-Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Sidebar for API key and debugging options
st.sidebar.title("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your API Key", type="password")

# Debugging options in sidebar
st.sidebar.title("🔧 Debug Options")
debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=False)
# Initialize test_mode regardless of debug_mode setting
test_mode = False
if debug_mode:
    image_max_size = st.sidebar.slider("Max Image Dimension", 256, 2048, 1024, 128)
    image_quality = st.sidebar.slider("Image Quality", 50, 100, 85, 5)
    show_base64 = st.sidebar.checkbox("Show Base64 Preview", value=False)
    test_mode = st.sidebar.checkbox("Test Mode (Skip API Call)", value=False)

# App title and description
st.title("🎬 Kling Image-to-Video Generator")
st.markdown("Transform your images into motion videos with AI")

# Helper functions
def resize_image(image, max_size=1024):
    """Resize image while maintaining aspect ratio."""
    width, height = image.size
    if width > height:
        if width > max_size:
            new_width = max_size
            new_height = int(height * (max_size / width))
    else:
        if height > max_size:
            new_height = max_size
            new_width = int(width * (max_size / height))
        else:
            return image  # No resize needed
    
    return image.resize((new_width, new_height), Image.LANCZOS)

def convert_image_to_base64(image, format="JPEG", quality=85):
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format=format, quality=quality)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def fetch_image_from_url(url):
    """Fetch image from URL and return PIL Image object."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        st.error(f"Failed to fetch image from URL: {e}")
        return None

def validate_api_response(response):
    """Validate API response and extract error details."""
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get("error", "Unknown error")
            return False, f"API Error ({response.status_code}): {error_message}"
        except:
            return False, f"API Error ({response.status_code}): {response.text[:200]}"
    return True, None

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    # Input method
    input_method = st.radio("Choose image input method:", ["Upload Image", "Image URL"])
    
    # Form inputs
    with st.form("kling_form"):
        # Image input
        image_data = None
        
        if input_method == "Upload Image":
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
            if uploaded_file:
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_container_width=True)
                    image_data = image
                except Exception as e:
                    st.error(f"Error opening image: {e}")
        else:
            image_url = st.text_input("Image URL", "https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg")
            if image_url:
                try:
                    st.image(image_url, caption="Image from URL", use_container_width=True)
                except:
                    st.error("Unable to display image from URL. Please check if the URL is valid.")
        
        # Video settings
        st.subheader("Video Generation Settings")
        prompt = st.text_area("Prompt", "Kitten riding in an aeroplane and looking out the window.")
        negative_prompt = st.text_area("Negative Prompt", "No sudden movements, no fast zooms.")
        
        # Additional parameters
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            duration = st.slider("Video Duration (seconds)", min_value=5, max_value=10, value=5, step=5)
        with col_b:
            version = st.selectbox("Kling Version", ["1.6", "1.5"])
        with col_c:
            cfg_scale = st.slider("CFG Scale", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
        
        # Fixed: Changed to use "std" or "pro" as required by API
        mode = st.selectbox("Processing Mode", ["pro", "std"])
        
        submitted = st.form_submit_button("🚀 Generate Video")

with col2:
    st.subheader("Generated Video")
    video_placeholder = st.empty()
    log_placeholder = st.empty()
    
    # Process submission
    if submitted:
        if not api_key and not test_mode:
            st.warning("⚠️ Please enter your API key in the sidebar.")
        else:
            # Prepare the image
            try:
                # Process the image based on input method
                if input_method == "Upload Image":
                    if uploaded_file and image_data:
                        # Use the already loaded image
                        image = image_data
                    else:
                        st.error("❌ Please upload an image.")
                        st.stop()
                else:
                    if image_url:
                        image = fetch_image_from_url(image_url)
                        if image is None:
                            st.error("❌ Failed to fetch image from URL.")
                            st.stop()
                    else:
                        st.error("❌ Please enter an image URL.")
                        st.stop()
                
                # Initialize variables for when debug mode is off
                if not debug_mode:
                    image_max_size = 1024
                    image_quality = 85
                
                # Resize image
                original_size = image.size
                image = resize_image(image, max_size=image_max_size)
                resized_size = image.size
                
                if debug_mode:
                    st.info(f"Image resized from {original_size} to {resized_size}")
                
                # Convert to base64
                base64_image = convert_image_to_base64(image, quality=image_quality)
                
                # Debug information
                if debug_mode:
                    log_placeholder.info(f"Image converted to base64 (length: {len(base64_image)} characters)")
                    if show_base64:
                        st.text_area("Base64 Preview", value=base64_image[:100] + "...", height=100)
                
                # Prepare API request
                url = "https://api.segmind.com/v1/kling-image2video"
                
                # Fixed: Ensure mode is either "std" or "pro" as required by API
                if mode not in ["std", "pro"]:
                    mode = "std"  # Default to "std" if somehow an invalid value is selected
                
                payload = {
                    "image": base64_image,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "cfg_scale": float(cfg_scale),
                    "mode": mode,  # This is now guaranteed to be "std" or "pro"
                    "duration": int(duration),  # This is already limited to 5 or 10 by the slider
                    "version": version
                }
                headers = {"x-api-key": api_key}
                
                # Debug payload
                if debug_mode:
                    payload_info = {k: v if k != "image" else f"[BASE64 string, length: {len(v)}]" for k, v in payload.items()}
                    st.json(payload_info)
                
                # Test mode or make actual API call
                if test_mode:
                    st.success("✅ Test Mode: API call skipped")
                    log_placeholder.info("In test mode, no API call was made")
                else:
                    with st.spinner("🚀 Generating video... This may take a minute."):
                        try:
                            log_placeholder.info("Sending request to Kling API...")
                            response = requests.post(url, json=payload, headers=headers, timeout=300)
                            
                            # Validate response
                            success, error_message = validate_api_response(response)
                            
                            if not success:
                                st.error(error_message)
                                
                                # More detailed error information for debugging
                                if debug_mode:
                                    st.write("Response Headers:", dict(response.headers))
                                    try:
                                        st.json(response.json())
                                    except:
                                        st.text(response.text)
                            else:
                                video_data = response.json()
                                video_url = video_data.get("video_url")
                                
                                if video_url:
                                    st.success("✅ Video generated successfully!")
                                    with video_placeholder:
                                        st.video(video_url)
                                    
                                    # Save video data
                                    video_bytes = requests.get(video_url).content
                                    st.download_button(
                                        label="📥 Download Video",
                                        data=video_bytes,
                                        file_name=f"kling_video_{int(time.time())}.mp4",
                                        mime="video/mp4"
                                    )
                                    
                                    # More response details in debug mode
                                    if debug_mode:
                                        st.json(video_data)
                                else:
                                    st.error("❌ Video URL not found in response.")
                                    if debug_mode:
                                        st.json(video_data)
                                        
                        except requests.exceptions.Timeout:
                            st.error("❌ Request timed out. The API server might be busy.")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Connection error. Please check your internet connection.")
                        except Exception as e:
                            st.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
                            if debug_mode:
                                st.exception(e)
                
            except Exception as e:
                st.error(f"❌ Error processing image: {type(e).__name__}: {e}")
                if debug_mode:
                    st.exception(e)

# Add a debugging section if debug mode is enabled
if debug_mode:
    st.subheader("🐞 Debug Information")
    if st.button("Test Connection to Kling API"):
        try:
            response = requests.get("https://api.segmind.com/v1/health", timeout=5)
            st.write("Status Code:", response.status_code)
            st.write("Response:", response.text)
        except Exception as e:
            st.error(f"Connection test failed: {e}")

# Footer
st.markdown("---")
st.markdown("Created with ❤️ | Powered by Kling API")
