import streamlit as st
import requests
import base64

# Convert image file to base64
def image_file_to_base64(file):
    image_data = file.read()
    return base64.b64encode(image_data).decode('utf-8')

# Convert image URL to base64
def image_url_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    else:
        raise Exception(f"Failed to fetch image: {response.status_code}")

# Streamlit app
st.set_page_config(page_title="Segmind Image2Video", layout="centered")
st.title("🎥 Segmind Kling 1.6 Image2Video")
st.markdown("Convert a single image to an AI-generated animated video using **Segmind's Kling 1.6** model.")

# API key input
api_key = st.text_input("🔑 Enter your Segmind API Key", type="password")

# Image input
st.subheader("🖼️ Image Input")
image_source = st.radio("Choose Image Source", ["Image URL", "Upload File"])
image_base64 = None

if image_source == "Image URL":
    image_url = st.text_input("Image URL *")
    if image_url:
        try:
            image_base64 = image_url_to_base64(image_url)
            st.image(image_url, caption="Image Preview")
        except Exception as e:
            st.error(str(e))
else:
    uploaded_file = st.file_uploader("Upload an image *", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image_base64 = image_file_to_base64(uploaded_file)
        st.image(uploaded_file, caption="Image Preview")

# Prompt fields
st.subheader("✏️ Animation Prompt")
prompt = st.text_input("Prompt", value="group of people talking to each other in an office setting")
negative_prompt = st.text_input("Negative Prompt", value="No sudden movements, no fast zooms.")

# Configuration fields
st.subheader("⚙️ Animation Settings")

cfg_scale = st.slider("CFG Scale (0-1)", min_value=0.0, max_value=1.0, value=0.5, step=0.1)

mode = st.selectbox("Mode", options=["pro", "standard", "fast"], index=0)

duration = st.selectbox("Duration (seconds)", options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], index=4)

# Submit button
if st.button("🎬 Generate Video"):
    if not api_key:
        st.error("API Key is required.")
    elif not image_base64:
        st.error("An image is required.")
    else:
        with st.spinner("Sending request to Segmind API..."):
            url = "https://api.segmind.com/v1/kling-1.6-image2video"
            headers = {"x-api-key": api_key}
            payload = {
                "image": image_base64,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "cfg_scale": cfg_scale,
                "mode": mode,
                "duration": int(duration)
            }

            response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            st.success("✅ Video generated successfully!")
            video_bytes = response.content
            st.video(video_bytes)
        else:
            st.error(f"❌ Failed to generate video ({response.status_code}): {response.text}")
