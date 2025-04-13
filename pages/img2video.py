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

# Only run if API key is provided
if api_key:
    url = "https://api.segmind.com/v1/kling-image2video"

    # Request payload
    data = {
        "image": image_url_to_base64("https://segmind-sd-models.s3.amazonaws.com/display_images/kling_ip.jpeg"),
        "prompt": "Kitten riding in an aeroplane and looking out the window.",
        "negative_prompt": "No sudden movements, no fast zooms.",
        "cfg_scale": 0.5,
        "mode": "pro",
        "duration": 5
    }

    headers = {'x-api-key': api_key}

    response = requests.post(url, json=data, headers=headers)
    st.write("Response:")
    st.code(response.content)
else:
    st.warning("Please enter your API key in the sidebar to proceed.")
