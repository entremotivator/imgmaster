import streamlit as st
import requests
import base64
from requests.exceptions import RequestException

# Initialize session state for API parameters
if 'api_params' not in st.session_state:
    st.session_state.api_params = {
        'api_key': "YOUR_API_KEY",
        'image': None,
        'prompt': "Kitten riding in an aeroplane",
        'negative_prompt': "No sudden movements",
        'cfg_scale': 0.5,
        'mode': "pro",
        'duration': 5
    }

# Sidebar configuration
with st.sidebar:
    st.header("API Configuration ⚙️")
    
    # API key input
    st.session_state.api_params['api_key'] = st.text_input(
        "🔑 API Key",
        value=st.session_state.api_params['api_key'],
        type="password"
    )
    
    # API parameters
    st.session_state.api_params['prompt'] = st.text_area(
        "Prompt",
        value=st.session_state.api_params['prompt'],
        help="Describe the desired video content"
    )
    
    st.session_state.api_params['negative_prompt'] = st.text_area(
        "Negative Prompt",
        value=st.session_state.api_params['negative_prompt'],
        help="Specify elements to avoid"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.api_params['cfg_scale'] = st.slider(
            "CFG Scale",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.api_params['cfg_scale'],
            step=0.1
        )
    with col2:
        st.session_state.api_params['duration'] = st.selectbox(
            "Duration (sec)",
            options=[5, 10],
            index=0 if st.session_state.api_params['duration'] == 5 else 1
        )
    
    st.session_state.api_params['mode'] = st.selectbox(
        "Quality Mode",
        options=["pro", "std"],
        index=0 if st.session_state.api_params['mode'] == "pro" else 1
    )

# Main content area
st.title("AI Video Generation 🎥")
st.markdown("Convert images to videos using Segmind's Kling API")

# Image input section
image_source = st.radio("Image Source", ["URL", "Upload"], horizontal=True)

if image_source == "URL":
    image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
    if image_url:
        try:
            st.image(image_url, caption="Input Image", use_container_width=True)
            st.session_state.api_params['image'] = base64.b64encode(
                requests.get(image_url).content
            ).decode('utf-8')
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
else:
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        st.session_state.api_params['image'] = base64.b64encode(
            uploaded_file.read()
        ).decode('utf-8')

# Generation button with session state persistence
if st.button("Generate Video 🎬", type="primary"):
    if not st.session_state.api_params['image']:
        st.error("Please provide an image first!")
    elif not st.session_state.api_params['api_key']:
        st.error("API key is required!")
    else:
        with st.spinner("Generating video (this may take 1-2 minutes)..."):
            headers = {'x-api-key': st.session_state.api_params['api_key']}
            
            try:
                response = requests.post(
                    "https://api.segmind.com/v1/kling-image2video",
                    json=st.session_state.api_params,
                    headers=headers,
                    timeout=120
                )
                
                if response.status_code == 200:
                    st.success("Video generated successfully!")
                    st.video(response.content)
                    
                    # Download button
                    st.download_button(
                        "Download Video",
                        data=response.content,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    st.json(response.json())
            
            except RequestException as e:
                st.error(f"Request failed: {str(e)}")
                st.code(f"Last parameters used:\n{st.session_state.api_params}", language='json')
