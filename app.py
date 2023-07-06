'''
    app.py
    Matt Ozborn - 06/10/23

    This is a program written in python that sets up a Flask application to handle
    document-based queries. It employs the langchain library to facilitate queries
    from users, returning both a generated response and the relevant source materials.
    The application exposes API endpoints to return this answer and relevant source 
    text chunks and another for serving the pdf documents that were initially 
    ingested to create the vector database.
'''


# Import necessary modules and classes
import os

from langchain.vectorstores.chroma import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import HumanMessage, AIMessage

from flask import Flask, render_template, request, jsonify, send_from_directory

from dotenv import load_dotenv


def make_chain():

    ''' Function to set up the AI model and retrieval chain.

    :return: The retrieval chain consisting of the AI model and vector retriever. '''

    # Initialize the AI model
    model = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature="1",
        # verbose=True
    )

    # Initialize the text embedding function
    embedding = OpenAIEmbeddings()

    # Initialize the vector store for document embeddings
    vector_store = Chroma(
        collection_name="chromadb",
        embedding_function=embedding,
        persist_directory=os.getenv("VECTORDB_DIR"),
    )

    # Return the retrieval chain with the AI model and vector retriever
    return ConversationalRetrievalChain.from_llm(
        model,
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
        # verbose=True
    )


# Create a new Flask application instance
app = Flask(__name__)

# Load environment variables
load_dotenv()


# Specify 'GET' and 'POST' requests to the root URL to be handled by query()
@app.route('/', methods=['GET','POST'])
def query():

    ''' Function to handle incoming requests to the root domain of the application.

    :return: The rendered HTML content or the query response data. '''

    # Returns the response data to a 'POST' request
    if request.method == "POST":
        # Initialize the retrieval chain
        chain = make_chain()

        # Initialize the chat history
        # TODO: required by the retrieval chain? circumvent?
        chat_history = []

        question = request.form["question"]

        # Generate response using the retrieval chain
        response = chain({"question": question, "chat_history": chat_history})

        # Retrieve answer and source material from the response
        answer = response["answer"]
        source = response["source_documents"]

        # Convert source_documents to JSON-serializable format
        source_documents_serializable = [doc.__dict__ for doc in source]

        # Add the question and answer to the chat history
        #chat_history.append(HumanMessage(content=question))
        #chat_history.append(AIMessage(content=answer))

        # Prepare the response data
        response_data = {
            "answer": answer,
            "source_documents": source_documents_serializable
        }

        # Convert python objects into a JSON-formatted response
        return jsonify(response_data)

    # Return the rendered HTML content
    return render_template("index.html")


from flask import request

@app.route('/data/docs/<path:filename>', methods=['GET', 'POST'])
def handle_document(filename):
    if request.method == 'GET':
        # Perform actions for GET request
        return send_from_directory('data/docs', filename)
    elif request.method == 'POST':
        # TODO: Perform actions for POST request
        # Call ingest.py script to parse the new document
        # Update the chroma database to reflect the new document
        return "POST request handled successfully"

if __name__ == "__main__":
    app.run(debug=True)