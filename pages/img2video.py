
import streamlit as st
import requests
import base64
import logging

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
    except requests.exceptions.RequestException as e:
        st.error(f"Image download failed: {str(e)}")
        return None

# Streamlit app configuration
st.set_page_config(page_title="Segmind Image2Video", layout="centered")
st.title("🎥 Segmind Kling 1.6 Image2Video")
st.markdown("Convert images to AI-generated videos using **Segmind's Kling 1.6** model.")

# API key input
api_key = st.text_input("🔑 Enter your Segmind API Key", type="password")

# Image input section
st.subheader("🖼️ Image Input")
image_source = st.radio("Choose Image Source", ["Image URL", "Upload File"])
image_base64 = None

if image_source == "Image URL":
    image_url = st.text_input("Image URL *", placeholder="https://example.com/image.jpg")
    if st.button("Preview URL Image") and image_url:
        try:
            st.image(image_url, caption="Image Preview", use_column_width=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    if image_url:
        image_base64 = image_url_to_base64(image_url)
else:
    uploaded_file = st.file_uploader("Upload an image *", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image_base64 = image_file_to_base64(uploaded_file)
        if image_base64:
            st.image(uploaded_file, caption="Uploaded Image Preview", use_column_width=True)

# Animation settings
st.subheader("✏️ Animation Settings")
col1, col2 = st.columns(2)
with col1:
    prompt = st.text_input("Prompt", value="group of people talking in an office", 
                          help="Describe the desired animation")
with col2:
    negative_prompt = st.text_input("Negative Prompt", value="No sudden movements, no fast zooms",
                                   help="Elements to avoid in the animation")

st.subheader("⚙️ Advanced Settings")
cfg_scale = st.slider("CFG Scale (guidance strength)", 0.0, 1.0, 0.5, 0.1,
                     help="Higher values follow prompt more strictly")
mode = st.selectbox("Quality Mode", options=["pro", "standard", "fast"], index=0,
                   help="Pro mode for highest quality, fast for quick results")
duration = st.selectbox("Duration (seconds)", options=list(range(1, 11)), index=4,
                       format_func=lambda x: f"{x}s")

# Video generation
if st.button("🎬 Generate Video", type="primary"):
    if not api_key:
        st.error("API Key is required")
    elif not image_base64:
        st.error("Please provide a valid image")
    else:
        with st.spinner("Generating video - this may take 1-2 minutes..."):
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "image": image_base64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": cfg_scale,
                "mode": mode,
                "duration": int(duration)
            }

            try:
                # Try both potential endpoints
                endpoints = [
                    "https://api.segmind.com/v1/kling-image2video",
                    "https://api.segmind.com/v1/kling-1.6-image2video"
                ]
                
                response = None
                for endpoint in endpoints:
                    try:
                        response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
                        if response.status_code == 200:
                            break
                    except requests.exceptions.RequestException:
                        continue

                if response and response.status_code == 200:
                    st.success("✅ Video generated successfully!")
                    try:
                        st.video(response.content, format="video/mp4")
                        st.download_button("Download Video", response.content, 
                                         file_name="generated_video.mp4")
                    except Exception as e:
                        st.error(f"Video display error: {str(e)}")
                        st.code(response.text[:500])  # Show partial response for debugging
                
                else:
                    error_message = f"""
                    ❌ Video generation failed ({response.status_code if response else 'No Response'}):
                    {response.text if response else 'Check your network connection'}
                    """
                    st.error(error_message)
                    
                    # Debugging information
                    with st.expander("Debug Details"):
                        st.write("**Request Payload:**")
                        st.json({k: (v[:100] + "..." if isinstance(v, str) and len(v) > 100 else v) 
                               for k, v in payload.items()})
                        
                        if response:
                            st.write("**API Response:**")
                            st.code(response.text[:1000])

            except Exception as e:
                st.error(f"Critical error: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.caption("Note: Video generation typically takes 30-120 seconds depending on settings")
