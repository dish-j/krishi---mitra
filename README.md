# Farmer Advisor Chatbot 🌾

A multilingual RAG chatbot for sustainable agriculture in India, supporting Hindi, Marathi, Tamil, Telugu and English.

## Features

- Multilingual support (auto-detection and translation)
- Retrieval-Augmented Generation (RAG) from agricultural dataset
- Conversation history stored in SQLite
- User-friendly Gradio interface

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

Run the chatbot:
```bash
python chatbot.py
```

The web interface will launch at `http://localhost:7860`

## Configuration

- Edit `farmer_advisor_dataset.csv` to add more agricultural knowledge
- Supported languages: Hindi (hi), Marathi (mr), Tamil (ta), Telugu (te), English (en)

## Database Schema

Interactions are stored in `chatbot.db` with the following structure:
- id: Unique interaction ID
- name: User name (optional)
- location: User location (optional)
- preferred_language: User's selected language
- query: Original question
- response: Generated answer
- timestamp: Interaction time

## Future Improvements

- Add more regional language support
- Include image recognition for plant diseases
- Implement voice input/output
