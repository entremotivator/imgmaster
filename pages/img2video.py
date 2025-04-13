import streamlit as st
import requests
import base64

# Convert an image file object to base64
def image_file_to_base64(file):
    image_data = file.read()
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
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
    prompt = st.text_input("Prompt", "Kitten riding in an aeroplane and looking out the window.")
    submitted = st.form_submit_button("Generate")

    if submitted and uploaded_file is not None:
        st.session_state.submitted = True
        st.session_state.uploaded_file = uploaded_file
        st.session_state.prompt = prompt

# Run only if form submitted and API key is provided
if st.session_state.submitted and api_key:
    url = "https://api.segmind.com/v1/kling-image2video"

    image_base64 = image_file_to_base64(st.session_state.uploaded_file)

    data = {
        "image": image_base64,
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

