/*
*   interact.js
*   Matt Ozborn - 06/10/23
*
*   This is a javascript program that manages the submission of document-based queries
*   to a Flask application and handles the returned responses. It's main function is
*   to take a user's question as input, send it via a 'POST' request to the server,
*   and then process the server's response. It processes the responses by displaying
*   it back into the structure of the html document.
*
*/


const questionElement = document.getElementById('question-input');
const sourcesElement = document.getElementById('source-documents');
const submitButton = document.getElementById('submit-button');
submitButton.addEventListener('click', handleSubmit);


/* TODO: Create visual feedback to the user that the query is being processed

const busySpinner = document.getElementById("busy-spinner");

function toggleBusy() {
    if (busySpinner.style.display === "block") {
        busySpinner.style.display = "none";
    }
    else {
        busySpinner.style.display = "block";
    }
} */


function handleSubmit(event) {

    /*
    *    This function handles the submission of the input form. It is called when the
    *    form is submitted and uses the input to fetch the response and source documents.
    *    After this, it formats the information to be populated back into the html.
    */ 

    // Prevent default form submission behavior
    event.preventDefault();

    // Collect the input question from the search component
    const question = questionElement.value;

    // Tidy up the input form
    questionElement.textContent = '';
    //toggleBusy()

    // Generate 'POST' request to the server with input question as a parameter
    fetch('/', {
        method: 'POST',
        body: new URLSearchParams({question}),
    })
        .then(response => response.json())
        .then(data => {
            //console.log(data);  //debug: print fetched data to console

            // Create variables to store the fetched data
            const answer = data.answer;
            const sourceDocuments = data.source_documents;

            // Display the answer in the appropriate html element
            const answerElement = document.getElementById('answer'); 
            answerElement.textContent = answer;

            // Loop through each of the fetched source-documents
            sourceDocuments.forEach((doc, index) => {
                const fileName = doc.metadata.file_name;
                const filePath = "/data/docs/" + fileName;
                const textChunk = "..." + doc.page_content.substring(0, 240) + "...";

                // Create the content to add to the target div
                const sourceContent = `
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">Source ${index + 1}: ${fileName}</h6>
                            <p class="card-text">${textChunk}</p>
                            <a href="${filePath}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">Go To File</a>
                        </div>
                    </div>
                `;
                
                // Add the content to the appropriate html div element
                const targetDivId = 'card' + (index + 1);
                const targetDiv = document.getElementById(targetDivId);
                targetDiv.innerHTML = sourceContent;
            });

            //toggleBusy();
        });
}