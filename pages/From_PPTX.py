import streamlit as st
from pathlib import Path
import llama_index
import os

from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, download_loader
import openai
from streamlit_chat import message as st_message

import PyPDF2

# AudioTranscriber = download_loader("AudioTranscriber")

# Replace the web scraper with PPTX upload functionality
PptxReader = download_loader("PptxReader")

web_dir = Path("Web")
web_dir.mkdir(exist_ok=True)

# Streamlit app code
st.title("Chat with Knowledge from Uploaded PPTX Content")

with st.expander("Upload PPTX"):
    # Upload field for the PPTX file
    pptx_file = st.file_uploader("Upload a PPTX file")

    # Button to initiate the PPTX upload process
    upload_pptx = st.button("Upload PPTX")

    if upload_pptx:
        if pptx_file is not None:
            loader = PptxReader()
            documents = loader.load_data(file=pptx_file)
            st.success(f"PPTX content uploaded successfully!")

            index = GPTSimpleVectorIndex.from_documents(documents)
            index.save_to_disk(f"pptx.json")

inp = st.text_input("Ask question")
ask = st.button("Submit")

if ask:
    # Load the index file from disk if it exists
    if os.path.isfile(f"pptx.json"):
        index = GPTSimpleVectorIndex.load_from_disk(f"pptx.json")
        res = index.query(inp)
        st.write(res)
    else:
        st.warning(
            "No index files found. Please upload a PPTX file above and wait for it to finish processing to create the index.")


# openai.api_key = os.getenv("API_KEY")
PDFReader = download_loader("PptxReader")
loader = PDFReader()


# favicon = "favicon.ac8d93a.69085235180674d80d902fdc4b848d0b (1).png"
#st.set_page_config(page_title="PDFbot Virtual Assistant", page_icon=None)


openai.api_key = os.getenv("API_KEY")

if "history" not in st.session_state:
    st.session_state.history = []


# Define a function to display the contents of a PDF file
def display_pdf(DATA_DIR, pdf_file):
    with open(os.path.join(DATA_DIR, pdf_file), "rb") as f:
        pdf_reader = PyPDF2.PdfFileReader(f)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            with st.expander(f"Page {page_num+1}"):
                st.write(page.extractText())

# Define a function to delete a PDF file and its corresponding JSON index file


def delete_file(DATA_DIR, file_name):
    pdf_path = os.path.join(DATA_DIR, file_name)
    json_path = os.path.join(
        DATA_DIR, os.path.splitext(file_name)[0] + ".json")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        st.success(f"File {file_name} deleted successfully!")
    else:
        st.error(f"File {file_name} not found!")
    if os.path.exists(json_path):
        os.remove(json_path)

# Define a function to save the uploaded file to the data directory


def save_uploaded_file(uploaded_file):
    with open(os.path.join(DATA_DIR, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


def new_chat():
    """
    Clears session state and starts a new chat.
    """
    st.session_state.history = []


DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

with st.expander("Manage_Books"):
    st.subheader("PDF document Management Portal")
    # Create a file uploader widget
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    # Check if a file was uploaded
    if uploaded_file is not None:
        # Save the uploaded file to the data directory
        save_uploaded_file(uploaded_file)
        st.success("It would take a while to index the books, please wait..!")

    # Create a button to create the index
    # if st.button("Create Index"):
        # Get the filename of the uploaded PDF
        pdf_filename = uploaded_file.name

        # Load the documents from the data directory
        documents = SimpleDirectoryReader(DATA_DIR).load_data()

        # Create the index from the documents
        index = GPTSimpleVectorIndex.from_documents(documents)

        # Save the index to the data directory with the same name as the PDF
        index.save_to_disk(os.path.join(
            DATA_DIR, os.path.splitext(pdf_filename)[0] + ".json"))
        st.success("Index created successfully!")

    # Get a list of files in the directory
    files = os.listdir(DATA_DIR)

    # Filter out the JSON index files
    files = [f for f in files if not f.endswith(".json")]

    colms = st.columns((4, 1, 1))

    fields = ["Name", 'View', 'Delete']
    for col, field_name in zip(colms, fields):
        # header
        col.subheader(field_name)

    i = 1
    for Name in files:
        i += 1
        col1, col2, col3 = st.columns((4, 1, 1))
        # col1.write(x)  # index
        col1.caption(Name)  # email
        if Name.endswith(".pdf"):
            col2.button("View", key=Name, on_click=display_pdf,
                        args=(DATA_DIR, Name))  # unique ID
            delete_status = True
        else:
            col2.write("N/A")
            delete_status = False
        button_type = "Delete" if delete_status else "Gone"
        button_phold = col3.empty()  # create a placeholder
        do_action = button_phold.button(
            button_type, key=i, on_click=delete_file, args=(DATA_DIR, Name))


# Get a list of available index files in the data directory
index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]


if index_filenames:
    # If there are index files available, create a dropdown to select the index file to load
    index_file = st.selectbox("Select an index file to load:", index_filenames)
    index_path = os.path.join(DATA_DIR, index_file)
    index = GPTSimpleVectorIndex.load_from_disk(index_path)
else:
    # If there are no index files available, prompt the user to upload a PDF file
    st.warning(
        "No index files found. Please upload a PDF file to create an index.")


def generate_answer():
    user_message = st.session_state.input_text
    query_str = str(user_message)
    message_bot = index.query(
        query_str, response_mode="compact", mode="embedding")
    st.session_state.history.append({"message": user_message, "is_user": True})
    st.session_state.history.append(
        {"message": str(message_bot), "is_user": False})
    st.session_state.input_text = ""
    # st.session_state.history = [{"message": user_message, "is_user": True},
    #                             {"message": str(message_bot), "is_user": False}]


if st.sidebar.button("New Chat"):
    new_chat()


input_text = st.text_input("Ask PDF_BOT Virtual Assitant a question",
                           key="input_text", on_change=generate_answer)

if st.session_state.history:
    chat = st.session_state.history[-1]
    st_message(**chat)

for chat in st.session_state.history:

    if chat["is_user"]:

        st.sidebar.caption("Question: " + chat["message"])
    else:
        with st.sidebar.expander("Bot Answer", expanded=False):
            st.write(chat["message"], language=None)


def st_message(message, is_user):
    if is_user:
        st.write("You: " + message)
    else:
        st.write("PDF_BOT: " + message)
