# REQUIRED IMPORTS
# REQUIRED IMPORTS
import streamlit as st
import requests
import base64
import io
from PIL import Image
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
st.title("Image to Video Generator")
st.markdown("Convert images to videos using AI")

# File uploader section
uploaded_file = st.file_uploader("Upload image (JPEG/PNG)", 
                               type=["jpg", "jpeg", "png"],
                               help="Maximum size: 5MB")

# URL input section
image_url = st.text_input("Or enter image URL:", 
                         value="https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg",
                         disabled=bool(uploaded_file),
                         help="Direct image URL required")

# Image display and processing
image_b64 = None
if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption='Uploaded Image', 
                use_container_width=True)
    with col2:
        image_b64 = image_file_to_base64(uploaded_file)
        if image_b64:
            st.success("Image processed successfully")
            st.code(f"Base64 length: {len(image_b64)//1000} KB", language="text")
            
elif image_url:
    try:
        st.image(image_url, caption='URL Image', 
                use_container_width=True)
        image_b64 = image_url_to_base64(image_url)
        if not image_b64:
            st.error("Failed to process URL image")
    except Exception as e:
        st.error(f"Image display error: {str(e)}")

# API Configuration Section
st.divider()
api_key = st.text_input("API Key", value="YOUR_API_KEY",
                       help="Get your API key from Segmind")
prompt = st.text_area("Prompt", 
                     value="Kitten riding in an aeroplane and looking out the window.",
                     height=100)
negative_prompt = st.text_area("Negative Prompt", 
                              value="No sudden movements, no fast zooms.",
                              height=100)

# Generation button with validation
if st.button("Generate Video", type="primary"):
    if not image_b64:
        st.error("Please provide a valid image first")
    elif api_key == "YOUR_API_KEY":
        st.error("Please enter a valid API key")
    else:
        with st.spinner("Generating video - this may take 1-2 minutes..."):
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
                    timeout=120  # Extended timeout for video generation
                )
                
                if response.status_code == 200:
                    st.success("Video generated successfully!")
                    st.download_button(
                        label="Download MP4",
                        data=response.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    
            except requests.Timeout:
                st.error("Generation timeout - please try again")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

# Debug section (can be removed in production)
with st.expander("Debug Info"):
    if image_b64:
        st.code(f"First 100 chars: {image_b64[:100]}...", language="text")
    st.write(f"Streamlit version: {st.__version__}")
    st.write(f"Pillow version: {Image.__version__}")
