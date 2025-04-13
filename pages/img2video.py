import streamlit as st
import requests
import base64
import logging
from requests.exceptions import RequestException

# Enable debug logging for requests
logging.basicConfig(level=logging.DEBUG)

# Convert image file to base64
def image_file_to_base64(file):
    try:
        image_data = file.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

# Convert image URL to base64
def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except RequestException as e:
        st.error(f"Image download failed: {str(e)}")
        return None

# Streamlit app configuration
st.set_page_config(page_title="Segmind Image2Video", layout="centered")
st.title("🎥 Segmind Kling 1.6 Image2Video")
st.markdown("Convert images to AI-generated videos using **Segmind's Kling 1.6** model.")

# API configuration
API_ENDPOINTS = [
    "https://api.segmind.com/v1/kling-image2video",
    "https://api.segmind.com/v1/kling-1.6-image2video",
]

# API key input
api_key = st.text_input("🔑 Enter your Segmind API Key", type="password", help="Get your API key from Segmind's dashboard")

# Image input section
st.subheader("🖼️ Image Input")
image_source = st.radio("Choose Image Source", ["Image URL", "Upload File"], horizontal=True)
image_base64 = None

if image_source == "Image URL":
    image_url = st.text_input("Image URL *", placeholder="https://example.com/image.jpg")
    if st.button("Preview URL Image") and image_url:
        try:
            st.image(image_url, caption="Image Preview", use_container_width=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    if image_url:
        image_base64 = image_url_to_base64(image_url)
else:
    uploaded_file = st.file_uploader("Upload an image *", type=["png", "jpg", "jpeg"], 
                                   help="Max 5MB recommended for best performance")
    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:  # 5MB limit
            st.warning("Large images may cause API timeouts. Consider resizing to under 5MB.")
        image_base64 = image_file_to_base64(uploaded_file)
        if image_base64:
            st.image(uploaded_file, caption="Uploaded Image Preview", use_container_width=True)

# Animation settings
st.subheader("✏️ Animation Settings")
col1, col2 = st.columns(2)
with col1:
    prompt = st.text_area("Prompt", value="group of people talking in an office", 
                         help="Be specific about motion directions (e.g., 'left to right pan')")
with col2:
    negative_prompt = st.text_area("Negative Prompt", value="No sudden movements, no fast zooms",
                                  help="Specify unwanted elements (e.g., 'blurry areas, distorted faces')")

st.subheader("⚙️ Advanced Settings")
col1, col2, col3 = st.columns(3)
with col1:
    cfg_scale = st.slider("CFG Scale", 0.0, 1.0, 0.5, 0.1,
                         help="Prompt adherence strength (0=creative, 1=strict)")
with col2:
    mode = st.selectbox("Quality Mode", options=["pro", "std"], index=0,
                       help="Pro: High quality, Std: Standard quality")
with col3:
    duration = st.selectbox("Duration", options=[5, 10], index=0,
                           format_func=lambda x: f"{x} seconds")

# Video generation
if st.button("🎬 Generate Video", type="primary", use_container_width=True):
    if not api_key:
        st.error("API Key is required")
    elif not image_base64:
        st.error("Please provide a valid image")
    else:
        with st.spinner("Generating video - this may take 1-2 minutes..."):
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Segmind-Streamlit/1.0"
            }
            
            payload = {
                "image": image_base64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": cfg_scale,
                "mode": mode,
                "duration": int(duration),
                "version": "1.6"  # Explicit version parameter
            }

            try:
                response = requests.post(
                    API_ENDPOINTS[0],  # Use primary endpoint
                    json=payload,
                    headers=headers,
                    timeout=(10, 120)  # Connect timeout 10s, read timeout 120s
                )

                if response.status_code == 200:
                    st.success("✅ Video generated successfully!")
                    try:
                        video_data = response.content
                        
                        # Display video
                        with st.container():
                            st.video(video_data, format="video/mp4")
                            
                            # Download section
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    "Download MP4",
                                    video_data,
                                    file_name="generated_video.mp4",
                                    mime="video/mp4"
                                )
                            with col2:
                                if st.button("Generate Another"):
                                    st.rerun()
                    
                    except Exception as e:
                        st.error(f"Video rendering error: {str(e)}")
                        st.code(f"Response headers: {dict(response.headers)}", language='text')
                
                else:
                    error_details = {
                        "status": response.status_code,
                        "headers": dict(response.headers),
                        "response": response.text[:1000]
                    }
                    
                    st.error(f"❌ Generation failed (HTTP {response.status_code})")
                    
                    with st.expander("Diagnostic Information"):
                        st.json({
                            "endpoint": API_ENDPOINTS[0],
                            "payload_keys": list(payload.keys()),
                            "image_size": f"{len(image_base64)//1024}KB",
                            "error_details": error_details
                        })
                    
                    if response.status_code == 401:
                        st.warning("Check your API key validity and permissions")
                    elif response.status_code == 406:
                        st.warning("Invalid parameters - ensure duration is 5/10s and mode is pro/std")
                    elif response.status_code == 413:
                        st.warning("Image too large - try resizing below 5MB")
                    elif response.status_code >= 500:
                        st.info("Server error - try again later or contact Segmind support")

            except RequestException as e:
                st.error(f"Network error: {str(e)}")
                st.progress(0, text="Retrying with alternative endpoint...")
                
                # Fallback to secondary endpoint
                try:
                    response = requests.post(
                        API_ENDPOINTS[1],
                        json=payload,
                        headers=headers,
                        timeout=120
                    )
                    if response.status_code == 200:
                        st.success("✅ Success on fallback endpoint!")
                        st.video(response.content)
                    else:
                        st.error(f"Fallback failed (HTTP {response.status_code})")
                except RequestException as e:
                    st.error(f"Critical failure: {str(e)}")

# Monitoring section
with st.expander("API Health Monitoring"):
    if 'request_history' not in st.session_state:
        st.session_state.request_history = []
    
    if st.button("Test API Connection"):
        test_payload = {
            "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",  # 1px transparent PNG
            "prompt": "test",
            "duration": 5,
            "mode": "std"
        }
        
        with st.spinner("Testing connectivity..."):
            try:
                test_response = requests.post(
                    API_ENDPOINTS[0],
                    json=test_payload,
                    headers={"x-api-key": api_key},
                    timeout=10
                )
                st.session_state.request_history.append({
                    "timestamp": st._get_report_ctx().request.utcnow.isoformat(),
                    "status": test_response.status_code,
                    "latency": test_response.elapsed.total_seconds()
                })
                
                st.metric("Last Test", 
                         f"HTTP {test_response.status_code}", 
                         f"{test_response.elapsed.total_seconds():.2f}s latency")
            
            except Exception as e:
                st.error(f"Connection test failed: {str(e)}")
    
    if st.session_state.request_history:
        st.write("Recent Requests:")
        st.dataframe(st.session_state.request_history[-5:])

# Footer
st.markdown("---")
st.caption("""
**Troubleshooting Tips**  
1. For 406 errors: Ensure duration is 5/10s and mode is pro/std  
2. For slow responses: Use 'std' mode with 5s duration  
3. For quality issues: Use 'pro' mode with detailed motion prompts  
""")
