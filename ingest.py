'''
    ingest.py
    Matt Ozborn - 06/09/23

    This is a program written in python that will take a directory full of 
    enterprise data documents and parse them into a vector database made up of
    embeddings that represents that original data. This is done so that, later 
    we can search through that data and return the relevant information for use
    with an AI chat bot.
'''


# Import necessary modules and classes
import pdfplumber
import re
import os
import sys

from typing import Callable, List, Tuple, Dict

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv


def extract_pages_from_pdf(file_path: str) -> List[Tuple[int, str]]:
    
    ''' Extracts the text from each page of the data files.

    :param file_path: The path to the data file document.
    :return: A list of tuples containing the page number and the extracted text. '''

    # Check to see if the file exists and throw error if it does not
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Open the file using pdfplumber
    with pdfplumber.open(file_path) as pdf:
        
        # Create an empty list to store the extracted page numbers and text
        pages = []
        
        # Loop through each page in the document and assign each page its number/index
        for page_num, page in enumerate(pdf.pages):

            # Extract the text from each page
            text = page.extract_text()

            # Check if extracted text is not empty
            if text.strip():
                
                # Append a tuple with the page number and corresponding text to the list
                pages.append((page_num + 1, text))
    
    # Returns the pages list
    return pages


def parse_pdf(file_path: str) -> List[Tuple[int, str]]:#, Dict[str, str]]:
    
    ''' Parses data by calling extraction functions for each page of the data files.
    
    :param file_path: The path to the data file document.
    :return: A tuple containing a list of tuples with page numbers, extracted text and metadata. '''
    
    # Check to see if the file exists and throw error if it does not
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Pass the file path as argument to extraction function and store the return into a variable
    pages = extract_pages_from_pdf(file_path)

    # Return the stored data
    return pages


''' Cleanup function for creating the final text that we will store in the db. '''
def merge_hyphenated_words(text: str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


''' Cleanup function for creating the final text that we will store in the db. '''
def fix_newlines(text: str) -> str:
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text)


''' Cleanup function for creating the final text that we will store in the db. '''
def remove_multiple_newlines(text: str) -> str:
    return re.sub(r"\n{2,}", "\n", text)


def clean_text(
    pages: List[Tuple[int, str]], cleaning_functions: List[Callable[[str], str]]
) -> List[Tuple[int, str]]:

    ''' Cleans up the resulting data after being parsed or extracted from the file.

    :param pages: The tuple from parse that includes page number and extracted text.
    :param cleaning_functions: List of cleanup functions to perform on the data.
    :return: List containing tuples made up of page numbers and resulting clean text. '''

    # Create an empty list to store the page numbers and cleaned text
    cleaned_pages = []
    
    # Loop through each tuple in the list of extracted data
    for page_num, text in pages:

        # Loop through each cleaning function in the list and store the result
        for cleaning_function in cleaning_functions:
            text = cleaning_function(text)
        
        # Store the resulting cleaned text back into the list
        cleaned_pages.append((page_num, text))
    
    # Return the list of stored data
    return cleaned_pages


def text_to_docs(text: List[str], file_name: str) -> List[Document]:
    
    ''' Converts list of cleaned text and the associated metadata to a list of Documents.

    :param text: List of the text returned from clean_text function.
    :param file_name: The name of the data file document.
    :return: List of the final Document chunks to be stored in the db. '''

    # Create an empty list to store the split document chunks
    doc_chunks = []

    # Loop through each tuple of cleaned data and split text into 1000 char chunks
    for page_num, page in text:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            separators=["\n\n", "\n", ".", "!", "\?", ",", " ", ""],
            chunk_overlap=200,
        )
        chunks = text_splitter.split_text(page)

        # Loop through chunks and create a Doc obj that incl. text chunk and metadata
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page_number": page_num,
                    "chunk": i,
                    "source": f"{file_name}-p{page_num}-{i}",
                    "file_name": file_name
                },
            )

            # Store the Doc obj in the list
            doc_chunks.append(doc)

    # Return the list of stored Documents
    return doc_chunks


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Define directory and resulting list of data filenames
    dir_path = os.getenv("DOCUMENT_DIR")
    pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]

    # Initialize a list to store document chunks to later pass to the vector db
    document_chunks = []

    # Loop through and process each file in the list
    for pdf_file in pdf_files:
        # Join the file name and directory path to create a complete file path
        file_path = os.path.join(dir_path, pdf_file)

        # Begin to parse the text from the pdf file
        print("Starting to process {}.".format(pdf_file))
        #raw_pages, metadata = parse_pdf(file_path)
        raw_pages = parse_pdf(file_path)

        # Create and cleanup the text chunks
        cleaning_functions = [
            merge_hyphenated_words,
            fix_newlines,
            remove_multiple_newlines,
        ]
        cleaned_text_pdf = clean_text(raw_pages, cleaning_functions)
        document_chunks += text_to_docs(cleaned_text_pdf, pdf_file)

        print("{} ready to be added to database.".format(pdf_file))

    # Generate embeddings and store them in a vector db
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(
        document_chunks,
        embeddings,
        collection_name="chromadb",
        persist_directory=os.getenv("VECTORDB_DIR")
    )

    # Save the db locally
    vector_store.persist()
    print("\nFinished creating new vector database.")