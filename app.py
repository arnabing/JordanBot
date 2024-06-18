import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI
from pathlib import Path
import base64

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.delta_generator.DeltaGenerator):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


def filter_documents(query, documents, top_n=3):
    """Filter documents based on the relevance to the query."""
    doc_texts = [doc.page_content for doc in documents]
    vectorizer = TfidfVectorizer().fit_transform(doc_texts + [query])
    vectors = vectorizer.toarray()
    query_vector = vectors[-1]
    doc_vectors = vectors[:-1]
    similarities = cosine_similarity([query_vector], doc_vectors)[0]
    top_indices = np.argsort(similarities)[-top_n:]
    return [documents[i] for i in top_indices]


def speak_text(text):
    """Convert text to speech using OpenAI's TTS and return the path to the audio file."""
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path


# Set up the Streamlit page configuration
st.set_page_config(page_title="Nike's Jordan Chatbot",
                   page_icon="👟", layout="wide")
st.title("Nike's Jordan Chatbot")

# Load and process CSV data
loader = CSVLoader(file_path="./products.csv")
documents = loader.load()

# Set up memory for contextual conversation
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

# Set up LLM and QA chain
llm = ChatOpenAI(model="gpt-4-turbo",
                 openai_api_key=openai_api_key, temperature=0, streaming=True)

# Set up the prompt template
prompt_template = PromptTemplate(
    input_variables=["chat_history", "question", "documents"],
    template="""
You are a chatbot designed to answer questions about Nike's Jordan shoes. Use the following information to answer the question as accurately as possible.

Conversation:
{chat_history}

Question:
{question}

Documents:
{documents}

Answer:
"""
)

# Set up the LLMChain
qa_chain = LLMChain(prompt=prompt_template, llm=llm)

# Set up Streamlit interface
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you with the Jordan shoes?"}]

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_query := st.chat_input(placeholder="Ask me anything about Jordan shoes!"):
    st.chat_message("user").write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Filter documents based on user query
    filtered_documents = filter_documents(user_query, documents)
    documents_content = "\n".join(
        [doc.page_content for doc in filtered_documents])

    # Format the prompt with the conversation history and the user's question
    prompt_input = {
        "chat_history": "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]),
        "question": user_query,
        "documents": documents_content
    }

    stream_handler = StreamHandler(st.empty())
    response = qa_chain(prompt_input, callbacks=[stream_handler])

    # Display the final answer
    answer = response.get(
        'text', 'I don\'t have enough information to answer that.')
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

    # # Display the image for the mentioned product
    # for doc in filtered_documents:
    #     product_id = doc.metadata.get('product_id', None)
    #     image_path = f"./images/{product_id}.jpg"
    #     if product_id and os.path.exists(image_path):
    #         st.image(image_path, caption=doc.metadata.get(
    #             'name', 'No Name'), use_column_width=True)
    #     else:
    #         st.write(f"Image not found for product: {
    #                  doc.metadata.get('name', 'Unknown')}")

    # Convert text to speech and play it
    speech_file_path = speak_text(answer)

    # Inject JavaScript to autoplay the audio and hide the player
    with open(speech_file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
    st.markdown(audio_html, unsafe_allow_html=True)
