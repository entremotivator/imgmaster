import streamlit as st
from PIL import Image
import datetime
import uuid
import io
import os

st.set_page_config(
    page_title="Image Upload and Management",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to handle image upload
def upload_image():
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        return image
    return None

# Function to save uploaded image
def save_uploaded_image(image, filename):
    image.save(filename)
    return filename

# Function to save image history and manage exports
def save_image(image_buffer, filename):
    try:
        with open(filename, 'wb') as f:
            f.write(image_buffer.getbuffer())
        return filename
    except IOError as e:
        return f"Error saving file: {e}"

def export_all_images(image_history):
    export_folder = os.path.join('outputs', uuid.uuid4().hex)
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    saved_files = []
    for item in image_history:
        file_path = os.path.join(export_folder, item['filename'])
        result = save_image(item['image'], file_path)
        if "Error" not in result:
            saved_files.append(result)

    return saved_files, export_folder

def main():
    st.title("Image Upload and Management")
    st.sidebar.image("assets/header.png")
    st.sidebar.title("Upload and Manage Images")
    
    # Image upload section in the sidebar
    uploaded_image = upload_image()
    
    if uploaded_image:
        # Save uploaded image to folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex
        filename = f"uploaded_image_{timestamp}_{unique_id}.jpeg"
        save_uploaded_image(uploaded_image, os.path.join('uploads', filename))
        st.sidebar.success(f"Image uploaded and saved as {filename}")
        
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Image history section
    if 'image_history' not in st.session_state:
        st.session_state.image_history = []

    # Check if the image history is updated (if an image was uploaded)
    if uploaded_image:
        # Create image buffer to hold the uploaded image
        img_buffer = io.BytesIO()
        uploaded_image.save(img_buffer, format="JPEG")
        img_buffer.seek(0)

        # Generate a unique filename for the uploaded image
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex
        filename = f"uploaded_image_{timestamp}_{unique_id}.jpeg"

        # Add the image to the session state history
        st.session_state.image_history.insert(0, {'image': img_buffer, 'filename': filename})
        st.session_state.image_history = st.session_state.image_history[:10]  # Keep the latest 10 images

    # Display and manage image history
    if st.session_state.image_history:
        current_image = st.session_state.image_history[0]['image']
        current_image.seek(0)  # Reset the buffer to the start
        st.image(current_image, use_column_width=True)

        st.sidebar.divider()

        # Save to 'outputs' folder and provide download link
        if st.sidebar.button('Save Current Image to Folder'):
            filename = st.session_state.image_history[0]['filename']
            save_result = save_image(current_image, os.path.join('outputs', filename))
            if "Error" in save_result:
                st.sidebar.error(save_result)
            else:
                st.sidebar.success(f"Image saved as {save_result}")

        # Button to export all images
        if st.sidebar.button('Export All Images'):
            saved_files, export_folder = export_all_images(st.session_state.image_history)
            if saved_files:
                st.sidebar.success(f"All images exported to {export_folder}")
            else:
                st.sidebar.error("Error exporting images")

        st.sidebar.divider()

if __name__ == "__main__":
    main()
