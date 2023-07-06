# Document-Based Query Handler Application

This application consists of a script to parse a directory of enterprise data documents and turn them into a vector database, a Flask application, which employs the `langchain` library to facilitate queries from users, and a JavaScript and HTML frontend, which handles the submission of queries and the presentation of responses.

### Files that make up the application:
- ingest.py    - Vector database creation script
- app.py       - Flask application backend
- interact.js  - Interface between the server backend and web ui
- index.html   - Web user interface

## Vector DB Creation Script - ingest.py

This is a python script that takes a directory full of enterprise data documents and parses them into a vector database made up of embeddings representing the original data. This enables us to search through that data and retrieve the most relevant information and allows us to work with a much smaller representation of the initial data.

### Requirements
- Python
- `dotenv`
- `pdfplumber`
- `langchain` package which includes `Document`, `RecursiveCharacterTextSplitter`, `Chroma`, `OpenAIEmbeddings`

### How to use:
1. Store your files in a directory.

2. Set your environment variables:
    - `DOCUMENT_DIR` should point to the directory where your PDF files are stored.
    - `VECTORDB_DIR` should point to the directory where you want to save the generated vector database.

3. Run the script:

    - ``` python3 ingest.py ```

## Backend - app.py

The backend is a Flask application that sets up a Conversational Retrieval Chain using the `langchain` library. The chain comprises an AI model (GPT-3.5-turbo), a vector store for document embeddings (`Chroma`), and a text embedding function (`OpenAIEmbeddings`).

The application exposes API endpoints to return both the answer and relevant source text chunks, and another for serving the PDF documents that were initially ingested to create the vector database.

### Key Functions

- `make_chain()`: Initializes the AI model and retrieval chain.
- `query()`: Handles incoming requests to the root domain of the application, returning either the rendered HTML content or the query response data.
- `get_document(filename)`: Handles incoming requests to the document storage location and returns the requested document.

## Frontend - index.html, interact.js

The frontend is made up of HTML/JavaScript and manages the submission of the input form. It takes a user's question as input, sends it via a 'POST' request to the server, and processes the server's response by displaying it back into the structure of the HTML document.

### Key Function

- `handleSubmit(event)`: Handles the submission of the input form, fetches the response and source documents, and formats the information to be populated back into the HTML.

## How to Use

1. Launch the Flask server.
2. Open the HTML page in a web browser.
3. Insert your query into the search bar and press submit.
4. The answer will be displayed, along with the relevant source documents.

## Installation and Setup

The environment variables needed to run the application can be set in a `.env` file. You need to specify the directory for the `Chroma` vector store in `VECTORDB_DIR`, the directory where your documents are located in `DOCUMENT_DIR`, and your OpenAI API key in `OPENAI_API_KEY`.

The frontend needs to be incorporated into an HTML document with the appropriate structure. A default html document is included but if you wish to change it, the HTML elements with the following ids are expected:
- 'question-input'
- 'source-documents'
- 'submit-button'
- 'answer'
- 'card' followed by the index of the source document (e.g., 'card1', 'card2', etc.)

`GET` requests to the root of app.py will render the index.html template located in `templates/`

## Default HTML Layout

The included HTML layout provides a basic user interface for submitting queries and displaying responses. It comprises several sections, including a header, a body for submitting queries and displaying responses, and a footer. The main input form for submitting queries resides in the body, along with the `div` elements for displaying the answer and source documents.