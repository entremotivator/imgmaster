import streamlit as st
import page  # Pulls additional content from /page.py

st.set_page_config(page_title="Mega Content Suite", layout="wide")

st.title("🎬 Mega Content Suite")
st.markdown("### The Ultimate Creator's Toolkit — Powered by AI ⚡")

st.markdown("""
Welcome to **Mega Content Suite** – your all-in-one creative studio. Whether you're a content creator, marketer, or entrepreneur, we've got the tools to turn your ideas into 🔥 multimedia masterpieces.

---

### 🚀 Key Features

- 📝 **Text-to-Video Generator**  
  Convert written scripts into stunning video content in seconds.

- 🖼️ **Image-to-Video Animator**  
  Transform static images into animated scenes with dynamic transitions.

- 🎙️ **Voiceover Integration**  
  Add realistic AI voiceovers to your content.

- 🧠 **Smart Script Assistant**  
  Get script suggestions, taglines, or ad copy with a single prompt.

- 🎨 **Content Templates**  
  Access ready-made templates for reels, ads, intros, and more.

- 🧰 **Drag-and-Drop Editor** *(Coming Soon)*  
  A fully interactive timeline editor for polishing your content.

- 📤 **One-Click Export**  
  Download or share content directly to social platforms.

---

""")

st.subheader("🔄 Dynamic Content from `/page`")
if hasattr(page, "render"):
    page.render()
else:
    st.warning("`page.py` is missing a `render()` function.")

st.divider()
st.markdown("✨ Let the Mega Content Suite turn your vision into viral-ready videos!")

