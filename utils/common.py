import streamlit as st
import requests
import base64
import os
import json
import time
from io import BytesIO
from PIL import Image

# Function to handle API key retrieval
def get_api_key():
    if 'api_key' in st.session_state and st.session_state['api_key']:
        return st.session_state['api_key']
    else:
        st.error("Please set your API key on the Home page first!")
        return None

# Function to convert image file to base64
def image_file_to_base64(file):
    return base64.b64encode(file.read()).decode('utf-8')

# Function to convert image URL to base64
def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        st.error(f"Error fetching image from URL: {str(e)}")
        return None

# Function to display image upload/URL input
def get_image_input(help_text="Upload an image or provide a URL"):
    image_source = st.radio("Select image source", ["Upload", "URL"], horizontal=True)
    image_base64 = None
    image_preview = None
    
    if image_source == "URL":
        url_input = st.text_input("Image URL", help=help_text)
        if url_input:
            with st.spinner("Fetching image..."):
                image_base64 = image_url_to_base64(url_input)
                if image_base64:
                    st.image(url_input, caption="Preview", use_column_width=True)
                    image_preview = url_input
    else:
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], help=help_text)
        if uploaded_file:
            image_base64 = image_file_to_base64(uploaded_file)
            st.image(uploaded_file, caption="Preview", use_column_width=True)
            image_preview = uploaded_file
    
    return image_base64, image_preview

# Function to make API request to Segmind
def make_segmind_api_request(endpoint, payload, api_key=None):
    if not api_key:
        api_key = get_api_key()
        if not api_key:
            return None, "API key not provided"
    
    headers = {"x-api-key": api_key}
    
    try:
        with st.spinner("Processing request..."):
            response = requests.post(f"https://api.segmind.com/v1/{endpoint}", json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.content, None
        else:
            return None, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return None, f"Request failed: {str(e)}"

# Function to save output to file
def save_output(data, file_extension):
    timestamp = int(time.time())
    filename = f"segmind_output_{timestamp}.{file_extension}"
    
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    
    file_path = os.path.join("outputs", filename)
    
    with open(file_path, "wb") as f:
        f.write(data)
    
    return file_path

# Function to show standardized result section
def show_result(result, error, file_extension="png"):
    if error:
        st.error(error)
        return
    
    if result:
        st.success("Generation successful!")
        
        if file_extension == "mp4":
            st.video(result)
        else:
            st.image(result)
        
        # Save button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Save Result"):
                file_path = save_output(result, file_extension)
                st.success(f"Saved to {file_path}")
        
        # Download button
        with col2:
            if file_extension == "png" or file_extension == "jpg":
                st.download_button(
                    label="Download Image",
                    data=result,
                    file_name=f"segmind_result.{file_extension}",
                    mime=f"image/{file_extension}"
                )
            elif file_extension == "mp4":
                st.download_button(
                    label="Download Video",
                    data=result,
                    file_name="segmind_result.mp4",
                    mime="video/mp4"
                )
