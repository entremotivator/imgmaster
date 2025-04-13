import streamlit as st
import requests
import base64

# Use this function to convert an image file from the filesystem to base64
def image_file_to_base64(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

# Use this function to fetch an image from a URL and convert it to base64
def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

# Sidebar input for API key
st.sidebar.title("API Settings")
api_key = st.sidebar.text_input("Enter your API Key", type="password")

# Initialize session state
if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.title("Kling Image-to-Video Generator")

# Streamlit form for user input
with st.form("kling_form"):
    image_url = st.text_input("Image URL", "https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg")
    prompt = st.text_input("Prompt", "Kitten riding in an aeroplane and looking out the window.")
    submitted = st.form_submit_button("Generate")

    if submitted:
        st.session_state.submitted = True
        st.session_state.image_url = image_url
        st.session_state.prompt = prompt

# Run only if form submitted and API key is provided
if st.session_state.submitted and api_key:
    url = "https://api.segmind.com/v1/kling-image2video"

    data = {
        "image": image_url_to_base64(st.session_state.image_url),
        "prompt": st.session_state.prompt,
        "negative_prompt": "No sudden movements, no fast zooms.",
        "cfg_scale": 0.5,
        "mode": "pro",
        "duration": 5
    }

    headers = {'x-api-key': api_key}

    with st.spinner("Generating video..."):
        response = requests.post(url, json=data, headers=headers)

    st.success("Response received:")
    st.code(response.content)
elif st.session_state.submitted and not api_key:
    st.warning("Please enter your API key in the sidebar.")

