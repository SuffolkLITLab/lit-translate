import os
import streamlit as st
import openai
from openai import OpenAI
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import tempfile
from markitdown import MarkItDown
md = MarkItDown()


# Configure OpenAI using environment variables
# TODO: The 'openai.api_base' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(base_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"))'
# openai.api_base = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

st.title("AI Text Translator")
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
