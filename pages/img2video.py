import streamlit as st
import requests
import base64
from PIL import Image
import io
import tempfile
import os
import time
import uuid

# Page config
st.set_page_config(
    page_title="Kling Image-to-Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Sidebar for API key
st.sidebar.title("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your API Key", type="password")

# App title and description
st.title("🎬 Kling Image-to-Video Generator")
st.markdown("Transform your images into motion videos with AI")

# Create temp directory if it doesn't exist
TEMP_DIR = os.path.join(tempfile.gettempdir(), "kling_app")
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to clean up old temp files (older than 1 hour)
def cleanup_temp_files():
    current_time = time.time()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
            os.remove(file_path)

# Helper functions
def save_uploaded_file(uploaded_file):
    """Save uploaded file to temp directory and return URL."""
    # Create unique filename
    file_extension = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(TEMP_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Return a URL-like path that could be used in your application
    # In a real app, this might be an actual URL to your server
    return file_path

def image_file_to_base64(file_path):
    """Convert image file to base64."""
    with open(file_path, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("utf-8")

def image_url_to_base64(image_url):
    """Fetch image from URL and convert to base64."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        st.error(f"❌ Failed to fetch image from URL: {e}")
        return None

# Clean up old temp files on app start
cleanup_temp_files()

# Main app layout
col1, col2 = st.columns([1, 1])

with col1:
    # Input method
    input_method = st.radio("Choose image input method:", ["Upload Image", "Image URL"])
    
    # Form inputs
    with st.form("kling_form"):
        temp_file_path = None
        image_url = None
        
        if input_method == "Upload Image":
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
            if uploaded_file:
                # Save the uploaded file and get the path
                temp_file_path = save_uploaded_file(uploaded_file)
                st.image(Image.open(uploaded_file), caption="Uploaded Image", use_container_width=True)
        else:
            image_url = st.text_input("Image URL", "https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg")
            if image_url:
                try:
                    st.image(image_url, caption="Image from URL", use_container_width=True)
                except:
                    st.error("Unable to display image from URL. Please check if the URL is valid.")
        
        st.subheader("Video Generation Settings")
        prompt = st.text_area("Prompt", "Kitten riding in an aeroplane and looking out the window.")
        negative_prompt = st.text_area("Negative Prompt", "No sudden movements, no fast zooms.")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            duration = st.slider("Video Duration (seconds)", min_value=5, max_value=10, value=5, step=5)
        with col_b:
            version = st.selectbox("Kling Version", ["1.6", "1.5"])
        with col_c:
            cfg_scale = st.slider("CFG Scale", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
        
        submitted = st.form_submit_button("🚀 Generate Video")

with col2:
    st.subheader("Generated Video")
    video_placeholder = st.empty()
    
    # Process submission
    if submitted:
        if not api_key:
            st.warning("⚠️ Please enter your API key in the sidebar.")
        else:
            base64_image = None
            if input_method == "Upload Image":
                if temp_file_path:
                    base64_image = image_file_to_base64(temp_file_path)
                else:
                    st.error("❌ Please upload an image.")
            else:
                if image_url:
                    base64_image = image_url_to_base64(image_url)
                else:
                    st.error("❌ Please enter an image URL.")
            
            if base64_image:
                url = "https://api.segmind.com/v1/kling-image2video"
                payload = {
                    "image": base64_image,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "cfg_scale": cfg_scale,
                    "mode": "pro",
                    "duration": duration,
                    "version": version
                }
                headers = {"x-api-key": api_key}
                
                with st.spinner("🚀 Generating video... This may take a minute."):
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
                                with video_placeholder:
                                    st.video(video_url)
                                
                                # Save video data
                                st.download_button(
                                    label="📥 Download Video",
                                    data=requests.get(video_url).content,
                                    file_name=f"kling_video_{int(time.time())}.mp4",
                                    mime="video/mp4"
                                )
                            else:
                                st.error("❌ Video URL not found in response.")
                    except Exception as e:
                        st.exception(f"❌ Unexpected error: {e}")

# Footer
st.markdown("---")
st.markdown("Created with ❤️ | Powered by Kling API")
