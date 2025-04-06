import sqlite3
import gradio as gr
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from googletrans import Translator
import openai
import pandas as pd
from datetime import datetime

# Initialize components
def initialize_components():
    # Load dataset
    data = pd.read_csv('farmer_advisor_dataset.csv')
    
    # Initialize SQLite database
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 location TEXT,
                 preferred_language TEXT,
                 query TEXT,
                 response TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    
    # Initialize FAISS vector store
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(data['advice'].tolist(), embeddings)
    
    return conn, vector_store

# Translation functions
def translate_to_english(text, src_lang='auto'):
    translator = Translator()
    return translator.translate(text, src=src_lang, dest='en').text

def translate_to_language(text, dest_lang):
    translator = Translator()
    return translator.translate(text, src='en', dest=dest_lang).text

# RAG response generation
def generate_response(query, vector_store):
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(query)
    
    # Format context from retrieved documents
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Generate response using OpenAI
    openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with actual API key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful agricultural advisor."},
            {"role": "user", "content": f"Question: {query}\n\nContext: {context}"}
        ]
    )
    return response['choices'][0]['message']['content']

# Main chat function
def chat(name, location, preferred_language, query, conn, vector_store):
    # Detect language if not specified
    if preferred_language.lower() == 'auto':
        translator = Translator()
        detected_lang = translator.detect(query).lang
        preferred_language = detected_lang
    
    # Translate query to English
    try:
        english_query = translate_to_english(query, preferred_language)
    except:
        english_query = query  # Fallback to original if translation fails
    
    # Generate response
    english_response = generate_response(english_query, vector_store)
    
    # Translate response back to original language
    try:
        final_response = translate_to_language(english_response, preferred_language)
    except:
        final_response = english_response  # Fallback to English if translation fails
    
    # Log interaction
    c = conn.cursor()
    c.execute("INSERT INTO interactions (name, location, preferred_language, query, response) VALUES (?, ?, ?, ?, ?)",
              (name, location, preferred_language, query, final_response))
    conn.commit()
    
    return final_response

# Gradio interface
def launch_interface(conn, vector_store):
    def wrapper(name, location, language, query):
        return chat(name, location, language, query, conn, vector_store)
    
    iface = gr.Interface(
        fn=wrapper,
        inputs=[
            gr.Textbox(label="Your Name (optional)"),
            gr.Textbox(label="Your Location (optional)"),
            gr.Dropdown(["hi", "mr", "ta", "te", "en"], label="Language", value="auto"),
            gr.Textbox(label="Your Question")
        ],
        outputs=gr.Textbox(label="Response"),
        title="🌾 Farmer Advisor Chatbot",
        description="Ask agricultural questions in your local language"
    )
    iface.launch()

if __name__ == "__main__":
    conn, vector_store = initialize_components()
    launch_interface(conn, vector_store)
