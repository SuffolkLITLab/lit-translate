import os
import streamlit as st
import openai
from openai import OpenAI
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"))
import tempfile
from markitdown import MarkItDown
md = MarkItDown()

st.set_page_config(
    page_icon="img/favicon.ico",
    page_title="LLM Text Translator by Suffolk LIT Lab",
)

LOGO = "img/lit-lab-logo-large.svg"
LOGO_ICON_IMAGE = "img/lit-favicon.svg"

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

st.logo(LOGO, size="large", icon_image=LOGO_ICON_IMAGE)
st.image(LOGO, use_container_width=True)
st.title("LLM Text Translator")
st.markdown("This AI-powered translator can convert text from one language to another.")
st.markdown("""Before you use this tool:
            
1. Redact sensitive or confidential information, like names of real people.
2. Always have a human translator review the output to ensure accuracy.
            
This tool uses the [OpenAI enterprise privacy policy](https://openai.com/enterprise-privacy/), which is appropriate for most sensitive uses. Data is never used for training purposes and you retain all rights.
""")
st.markdown("**AI-powered translation can make serious mistakes,** especially in translation of legal concepts, and should only be relied upon for a draft translation.")

st.write("Upload any file or paste text below, then choose a target language to translate the text.")

# Initialize input_text variable
input_text = ""

uploaded_file = st.file_uploader("Upload a file (TXT, DOCX, XLSX, etc.)")
if uploaded_file is not None:
    try:
        # Save the uploaded file to a temporary file
        ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_file_path = tmp_file.name

        # Convert file to text using MarkItDown
        result = md.convert(temp_file_path)
        input_text = result.text_content
        st.success("File converted successfully!")
    except Exception as e:
        st.error(f"Error converting file: {e}")
else:
    input_text = st.text_area("Or paste your text here:")

languages = [
    "Spanish", "Portuguese", "Chinese (Mandarin)", "Chinese (Cantonese)",
    "French", "Haitian Creole", "Vietnamese", "Khmer", "Arabic", "Russian", "Bengali",
    "Korean", "Tagalog", "Hindi", "Urdu", "Persian", "Italian", "Polish", "German", "Japanese", "Somali"
]

# Create a combobox-like widget by offering a selectbox with a custom option
options = languages + ["Other (Custom)"]
selected_language = st.selectbox("Select target language", options)

if selected_language == "Other (Custom)":
    selected_language = st.text_input("Enter custom target language", value="")

# Translation process
if st.button("Translate"):
    if not input_text.strip():
        st.error("Please provide some text to translate.")
    elif not selected_language.strip():
        st.error("Please select or enter a target language.")
    else:
        # Construct a prompt that requests markdown formatting in the output
        prompt = f"Translate the following text into {selected_language} and format the result in Markdown:\n\n{input_text}"
        try:
            with st.spinner("Translating..."):
                response = client.chat.completions.create(model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3)
            translated_text = response.choices[0].message.content.strip()

            translated_text = re.sub(r'^```(?:\w+)?\n', '', translated_text)
            translated_text = re.sub(r'\n```$', '', translated_text)

            st.subheader("Translation")
            # Render the translated Markdown as HTML
            st.markdown(translated_text, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.markdown("Built with ❤️ by [Suffolk Legal Innovation and Technology Lab](https://suffolklitlab.org)")