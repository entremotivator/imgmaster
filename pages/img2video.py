import streamlit as st
import requests
import base64
import logging
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Image conversion functions
def validate_base64(image_base64):
    try:
        base64.b64decode(image_base64, validate=True)
        return True
    except Exception as e:
        logger.error(f"Base64 validation failed: {str(e)}")
        return False

def image_file_to_base64(file):
    try:
        image_data = file.read()
        encoded = base64.b64encode(image_data).decode('utf-8')
        if not validate_base64(encoded):
            st.error("Invalid image encoding detected")
            return None
        return encoded
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        encoded = base64.b64encode(response.content).decode('utf-8')
        if not validate_base64(encoded):
            st.error("Invalid image encoding from URL")
            return None
        return encoded
    except RequestException as e:
        st.error(f"Image download failed: {str(e)}")
        return None

# Streamlit app configuration
st.set_page_config(page_title="Segmind Video Generator", layout="centered")
st.title("🎥 AI Video Generation")
st.markdown("Convert images to videos using Segmind's Kling 1.6 model")

# API configuration
API_ENDPOINTS = [
    "https://api.segmind.com/v1/kling-image2video",
    "https://api.segmind.com/v1/kling-1.6-image2video"
]

# API key input
api_key = st.text_input("🔑 Segmind API Key", type="password", 
                       help="Get your key from Segmind's dashboard")

# Image input section
st.subheader("🖼️ Image Input")
image_source = st.radio("Source", ["URL", "Upload"], horizontal=True, label_visibility="collapsed")

image_base64 = None
if image_source == "URL":
    image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
    if image_url:
        if st.button("Preview Image"):
            try:
                st.image(image_url, use_container_width=True)
            except Exception as e:
                st.error(f"Preview error: {str(e)}")
        image_base64 = image_url_to_base64(image_url)
else:
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.warning("For best results, use images under 5MB")
        image_base64 = image_file_to_base64(uploaded_file)
        if image_base64:
            st.image(uploaded_file, use_container_width=True)

# Generation parameters
st.subheader("⚙️ Animation Settings")

col1, col2 = st.columns(2)
with col1:
    prompt = st.text_area("Prompt", "A cat walking slowly", 
                         help="Describe the desired motion precisely")
with col2:
    negative_prompt = st.text_area("Negative Prompt", 
                                  "blurry, distorted, sudden movements",
                                  help="Elements to avoid in the animation")

col1, col2, col3 = st.columns(3)
with col1:
    cfg_scale = st.slider("Guidance Strength", 0.0, 1.0, 0.5, 0.1,
                         help="0 = Creative, 1 = Strict prompt following")
with col2:
    mode = st.selectbox("Quality", ["pro", "std"], index=0,
                       help="Pro: High quality, Std: Standard")
with col3:
    duration = st.selectbox("Duration", [5, 10], index=0,
                           format_func=lambda x: f"{x} seconds")

# Video generation
if st.button("🎬 Generate Video", type="primary", use_container_width=True):
    if not api_key:
        st.error("API key is required")
    elif not image_base64:
        st.error("Please provide a valid image")
    else:
        with st.spinner("Generating video..."):
            # Prepare request
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Segmind-Streamlit/1.2"
            }
            
            payload = {
                "image": image_base64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": cfg_scale,
                "mode": mode,
                "duration": duration,
                "version": "1.6"
            }

            # Log payload for debugging
            logger.info(f"Sending payload: { {k: (v[:100] + '...' if isinstance(v, str) and len(v) > 100 else v) for k, v in payload.items()} }")

            # Try endpoints sequentially
            response = None
            for endpoint in API_ENDPOINTS:
                try:
                    response = requests.post(
                        endpoint,
                        json=payload,
                        headers=headers,
                        timeout=(10, 120)  # 10s connect, 120s read
                    )
                    if response.status_code == 200:
                        break
                except RequestException as e:
                    logger.error(f"Endpoint {endpoint} failed: {str(e)}")
                    continue

            # Handle response
            if response and response.status_code == 200:
                st.success("Video generated successfully!")
                st.video(response.content)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download MP4",
                        response.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )
                with col2:
                    if st.button("Generate Another"):
                        st.rerun()
            
            else:
                error_details = {
                    "status": response.status_code if response else "No response",
                    "headers": dict(response.headers) if response else None,
                    "response": response.text if response else "Request failed"
                }
                
                st.error(f"Generation failed (Code: {error_details['status']})")
                
                with st.expander("Diagnostic Details"):
                    st.json({
                        "endpoint": API_ENDPOINTS[0],
                        "payload_keys": list(payload.keys()),
                        "image_size": f"{len(image_base64)//1024}KB",
                        "error_details": error_details
                    })

                # Specific error guidance
                if response and response.status_code == 400:
                    st.warning("""
                    Common 400 Error Fixes:
                    1. Verify image encoding (must be valid base64)
                    2. Ensure prompt doesn't contain special characters
                    3. Check API documentation for parameter requirements
                    """)
                elif response and response.status_code == 406:
                    st.warning("Ensure duration is 5/10s and mode is pro/std")
                elif response and response.status_code == 413:
                    st.warning("Image too large - try resizing below 5MB")

# Debugging section
with st.expander("🔧 API Diagnostics"):
    if st.button("Test Connection"):
        test_payload = {
            "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",  # 1px image
            "prompt": "test",
            "duration": 5,
            "mode": "std"
        }
        
        try:
            test_response = requests.post(
                API_ENDPOINTS[0],
                json=test_payload,
                headers={"x-api-key": api_key},
                timeout=10
            )
            st.metric("Test Result", 
                     f"HTTP {test_response.status_code}",
                     f"{test_response.elapsed.total_seconds():.2f}s")
        except Exception as e:
            st.error(f"Connection test failed: {str(e)}")

# Footer
st.markdown("---")
st.caption("""
**Troubleshooting Guide**  
1. For 400 errors: Check image encoding and prompt content  
2. For slow responses: Use 5s duration and 'std' mode  
3. For quality issues: Use detailed prompts with motion directions  
""")
