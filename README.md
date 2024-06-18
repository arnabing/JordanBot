# Nike's Jordan Chatbot

DEMO VIDEO -> https://www.loom.com/share/03a9c3a66f4c4a599c54105903d74905?sid=5ff37acc-d3c7-4495-9715-f7b29ae64319

This project is a Streamlit-based chatbot designed to answer questions about Nike's Jordan shoes. The chatbot uses OpenAI's GPT-3.5-turbo model to provide responses and leverages a CSV file containing product information to ensure accurate and specific answers. Additionally, the chatbot can speak its responses using OpenAI's text-to-speech capabilities and display images of the shoes.

## Features

- Scrapes Nike's website to gather product information and download images.
- Classifies images using GPT-4-turbo to obtain detailed attribute information.
- Answers questions about Nike's Jordan shoes using data from a CSV file.
- Displays product images when relevant.
- Speaks responses using text-to-speech.
- Maintains conversation context to provide coherent answers.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Firefox (for web scraping)

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/jordan-chatbot.git
   cd jordan-chatbot
   ```

2. **Create a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```sh
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Scraping and Classifying Data

1. **Run the web scraper:**
   This script scrapes Nike's website to gather product information and download images.

   ```sh
   python scrape.py
   ```

2. **Run the image classifier:**
   This script uses GPT-4-turbo to classify images and gather detailed attribute information.
   ```sh
   python classify_images.py
   ```

### Running the Chatbot

1. **Run the Streamlit app:**

   ```sh
   streamlit run app.py
   ```

2. **Access the chatbot:**
   Open your web browser and go to `http://localhost:8501`.

## Example .env File

Create a `.env` file in the root directory with the following content:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```
