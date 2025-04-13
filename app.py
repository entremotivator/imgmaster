import streamlit as st
import os
import importlib.util

st.set_page_config(page_title="Mega Content Suite", layout="wide")

st.title("🎬 Mega Content Suite")
st.markdown("### The Ultimate Creator's Toolkit — Powered by AI ⚡")

st.markdown("""
Welcome to **Mega Content Suite** – your all-in-one creative studio for content creation. Explore powerful tools and create stunning media from text or images!

---

### 🚀 Feature Highlights

- 📝 **Text-to-Video Generator**
- 🖼️ **Image-to-Video Animator**
- 🎙️ **AI Voiceovers**
- 🎬 **Smart Script Tools**
- 🎨 **Content Templates**
- 📤 **Quick Export & Sharing**

---

### 📂 Tools from `/page/`
""")

# Dynamically load and run all modules in the /page directory
page_dir = "page"
for filename in sorted(os.listdir(page_dir)):
    if filename.endswith(".py"):
        module_path = os.path.join(page_dir, filename)
        module_name = filename[:-3]  # remove .py extension
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "render"):
                st.markdown(f"#### 🧩 `{module_name.replace('_', ' ').title()}`")
                module.render()
                st.divider()
            else:
                st.warning(f"⚠️ `{module_name}.py` does not define a `render()` function.")
        except Exception as e:
            st.error(f"❌ Failed to load `{module_name}.py`: {e}")
