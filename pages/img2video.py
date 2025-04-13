import streamlit as st
import requests
import base64

# Image conversion functions
def image_file_to_base64(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

# Streamlit interface
st.title("Image to Video Generator")

# File uploader for local images
uploaded_file = st.file_uploader("Upload local image (or use URL below)", 
                                type=["jpg", "jpeg", "png"])

# URL input
image_url = st.text_input("Or enter image URL:", 
                         "https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg")

# Image display
if uploaded_file:
    st.image(uploaded_file, caption='Uploaded Image')
    image_b64 = image_file_to_base64(uploaded_file.name)
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
elif image_url:
    try:
        st.image(image_url, caption='URL Image')
        image_b64 = image_url_to_base64(image_url)
    except:
        st.error("Failed to load image from URL")

# API configuration
api_key = st.text_input("Enter API Key", "YOUR_API_KEY")
prompt = st.text_input("Enter Prompt", 
                      "Kitten riding in an aeroplane and looking out the window.")
negative_prompt = st.text_input("Negative Prompt", 
                               "No sudden movements, no fast zooms.")

# API request
if st.button("Generate Video"):
    if api_key == "YOUR_API_KEY":
        st.error("Please enter a valid API key")
    else:
        data = {
            "image": image_b64,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "cfg_scale": 0.5,
            "mode": "pro",
            "duration": 5
        }
        
        headers = {'x-api-key': api_key}
        response = requests.post(
            "https://api.segmind.com/v1/kling-image2video",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            st.success("Video generated successfully!")
            st.download_button(
                label="Download Video",
                data=response.content,
                file_name="generated_video.mp4",
                mime="video/mp4"
            )
        else:
            st.error(f"Generation failed: {response.text}")
