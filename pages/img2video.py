import streamlit as st
import requests
import base64
import io

def image_file_to_base64(uploaded_file):
    # Create in-memory bytes buffer
    bytes_buffer = io.BytesIO()
    
    # Convert image to RGB if needed (for PNG transparency handling)
    img = Image.open(uploaded_file).convert("RGB")
    
    # Save image to in-memory buffer
    img.save(bytes_buffer, format="JPEG")
    
    # Get bytes from buffer and encode
    image_bytes = bytes_buffer.getvalue()
    return base64.b64encode(image_bytes).decode('utf-8')

def image_url_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = response.content
        return base64.b64encode(image_data).decode('utf-8')
    return None

# Streamlit UI
st.title("Image to Video Generator")

# File uploader with enhanced error handling
uploaded_file = st.file_uploader("Upload image (JPEG/PNG)", 
                               type=["jpg", "jpeg", "png"])

# URL input with validation
image_url = st.text_input("Or enter image URL:", 
                         value="https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg",
                         disabled=bool(uploaded_file))

# Image preview and processing
image_b64 = None
if uploaded_file:
    try:
        # Display image preview
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
        
        # Process image through PIL
        image_b64 = image_file_to_base64(uploaded_file)
        
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        
elif image_url:
    try:
        st.image(image_url, caption='URL Image', use_column_width=True)
        image_b64 = image_url_to_base64(image_url)
        if not image_b64:
            st.error("Failed to download image from URL")
            
    except Exception as e:
        st.error(f"URL image loading error: {str(e)}")

# API Configuration
api_key = st.text_input("API Key", value="YOUR_API_KEY")
prompt = st.text_area("Prompt", 
                     value="Kitten riding in an aeroplane and looking out the window.")
negative_prompt = st.text_area("Negative Prompt", 
                              value="No sudden movements, no fast zooms.")

# Generation button with validation
if st.button("Generate Video"):
    if not image_b64:
        st.error("Please provide a valid image first")
    elif api_key == "YOUR_API_KEY":
        st.error("Please enter your API key")
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
