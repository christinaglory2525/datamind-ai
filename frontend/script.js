// ==========================================
// DataMind AI - Frontend JavaScript
// ==========================================

const API_URL = "/api/ask";

const questionInput = document.getElementById("question");
const sendButton = document.getElementById("sendBtn");
const chat = document.getElementById("chat");


// ==========================================
// SEND QUESntainer.innerHTML = htTION
// ==========================================

async function sendQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    // Add user's message
    addUserMessage(question);

    // Clear input
    questionInput.value = "";

    // Loading message
    const loadingId = "loading-" + Date.now();

    chat.insertAdjacentHTML(
        "beforeend",
        `
        <div class="message ai-message" id="${loadingId}">
            <div class="result-card">
                <h2>🤖 DataMind AI Analysis</h2>
                <p>Analyzing your database...</p>
                <div class="loading">
                    ⏳ Generating insights...
                </div>
            </div>
        </div>
        `
    );

    scrollToBottom();


    try {

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });


        if (!response.ok) {
            throw new Error(
                "Backend returned status " + response.status
            );
        }


        const result = await response.json();


        // Remove loading
        const loadingElement = document.getElementById(loadingId);

        if (loadingElement) {
            loadingElement.remove();
        }


        // Handle error
        if (!result.success && !result.diagram) {

            addAIMessage(`
                <div class="error">
                    ❌ ${escapeHtml(
                        result.error || "Something went wrong."
                    )}
                </div>
            `);

            return;
        }


        // Display result
        displayResult(result);
        scrollToLatestAnswer();

    }

    catch (error) {

        console.error("ERROR:", error);

        const loadingElement = document.getElementById(loadingId);

        if (loadingElement) {
            loadingElement.remove();
        }

        addAIMessage(`
            <div class="error">
                ❌ Could not connect to the AI backend.
                <br><br>
                Make sure FastAPI is running on:
                <strong>""</strong>
            </div>
        `);
    }

}


// ==========================================
// DISPLAY RESULT
// ==========================================

function displayResult(result) {

    let html = `

        <div class="message ai-message">

            <div class="result-card">

                <h2>🤖 DataMind AI Analysis</h2>

                <p>
                    I analyzed your database and found the following result.
                </p>

                <p class="question">
                    <strong>Question:</strong>
                    ${escapeHtml(result.question || "")}
                </p>
    `;


    // ======================================
    // GENERATED SQL
    // ======================================

    if (result.sql) {

        html += `

            <div class="section">

                <h3>🧠 Generated SQL</h3>

                <pre class="sql">${escapeHtml(result.sql)}</pre>

            </div>

        `;
    }


    // ======================================
    // QUERY RESULTS TABLE
    // ======================================

    if (
        result.data &&
        result.data.success &&
        Array.isArray(result.data.rows) &&
        result.data.rows.length > 0
    ) {

        const columns = result.data.columns || [];

        html += `

            <div class="section">

                <h3>📋 Query Results</h3>

                <div class="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                ${columns.map(column => `
                                    <th>
                                        ${escapeHtml(column)}
                                    </th>
                                `).join("")}

                            </tr>

                        </thead>


                        <tbody>

                            ${result.data.rows.map(row => `

                                <tr>

                                    ${columns.map(column => `

                                        <td>
                                            ${escapeHtml(row[column])}
                                        </td>

                                    `).join("")}

                                </tr>

                            `).join("")}

                        </tbody>

                    </table>

                </div>

            </div>

        `;
    }


    // ======================================
    // AI EXPLANATION
    // ======================================

    if (result.explanation) {

        html += `

            <div class="section explanation">

                <h3>💡 AI Explanation</h3>

                <p>
                    ${escapeHtml(result.explanation)}
                </p>

            </div>

        `;
    }


    // ======================================
    // VISUALIZATION
    // ======================================

    if (
        result.chart &&
        result.chart.success &&
        result.chart.url
    ) {

        let chartURL = result.chart.url;

        // Make sure URL works from frontend
        if (chartURL.startsWith("/")) {
            chartURL = "" + chartURL;
        }


        html += `

            <div class="section visualization-section">

                <h3>📊 Visualization</h3>

                <div class="visualization-container">

                    <iframe
                        src="${escapeHtml(chartURL)}"
                        class="visualization-frame"
                        title="Data Visualization"
                        loading="lazy">
                    </iframe>

                </div>

            </div>

        `;
    }


    // ======================================
    // ER DIAGRAM
    // ======================================

    if (
        result.diagram &&
        result.diagram.success &&
        result.diagram.url
    ) {

        let diagramURL = result.diagram.url;

        if (diagramURL.startsWith("/")) {
            diagramURL = "" + diagramURL;
        }


        html += `

            <div class="section er-section">

                <h3>🗂️ Database ER Diagram</h3>

                <p>
                    This diagram shows the tables and
                    relationships in your database.
                </p>


                <div class="er-container">

                    <iframe
                        src="${escapeHtml(diagramURL)}"
                        class="er-frame"
                        title="Database ER Diagram"
                        loading="lazy">
                    </iframe>

                </div>

            </div>

        `;
    }


    // ======================================
    // CLOSE CARD
    // ======================================

    html += `

            </div>

        </div>

    `;


    chat.insertAdjacentHTML("beforeend", html);

    scrollToBottom();
}


// ==========================================
// ADD USER MESSAGE
// ==========================================

function addUserMessage(question) {

    const html = `

        <div class="message user-message">

            <div class="user-bubble">

                ${escapeHtml(question)}

            </div>

        </div>

    `;

    chat.insertAdjacentHTML("beforeend", html);

    scrollToBottom();
}


// ==========================================
// ADD AI MESSAGE
// ==========================================

function addAIMessage(content) {

    const html = `

        <div class="message ai-message">

            <div class="result-card">

                ${content}

            </div>

        </div>

    `;

    chat.insertAdjacentHTML("beforeend", html);

    scrollToBottom();
}


// ==========================================
// EXAMPLE QUESTIONS
// ==========================================

function askExample(question) {

    questionInput.value = question;

    sendQuestion();

}


// ==========================================
// NEW CHAT
// ==========================================

function newChat() {

    chat.innerHTML = `

        <div class="welcome">

            <div class="welcome-icon">
                🧠
            </div>

            <h2>
                Ask your database anything
            </h2>

            <p>
                I can query your database, generate visualizations,
                and explain the results.
            </p>


            <div class="examples">

                <button
                    onclick="askExample(
                        'What are the top 5 products by revenue?'
                    )">
                    📈 Top 5 products by revenue
                </button>


                <button
                    onclick="askExample(
                        'Show me the products with the highest price'
                    )">
                    💰 Highest priced products
                </button>


                <button
                    onclick="askExample(
                        'How many customers are in each country?'
                    )">
                    🌍 Customers by country
                </button>


                <button
                    onclick="askExample(
                        'Show me the ER diagram of the database'
                    )">
                    🗂️ Database ER Diagram
                </button>

            </div>

        </div>

    `;

    questionInput.value = "";

}


// ==========================================
// ENTER KEY
// ==========================================

function handleKey(event) {

    // Enter = send
    // Shift + Enter = new line

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendQuestion();

    }

}


// ==========================================
// SCROLL CHAT TO BOTTOM
// ==========================================

function scrollToBottom() {

    setTimeout(() => {

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth"
        });

    }, 100);

}


// ==========================================
// HTML ESCAPE
// ==========================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}


// ==========================================
// BUTTON EVENT
// ==========================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendQuestion
    );

}


// ==========================================
// INPUT EVENT
// ==========================================

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        handleKey
    );

}
// AUTO SCROLL TO LATEST AI ANSWER
const autoScrollObserver = new MutationObserver(() => {
    setTimeout(() => {
        window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: "smooth"
        });
    }, 300);
});

if (resultContainer) {
    autoScrollObserver.observe(resultContainer, {
        childList: true,
        subtree: true
    });
}
function scrollToLatestAnswer() {
    const chat = document.getElementById("chat");

    if (chat) {
        chat.scrollTo({
            top: chat.scrollHeight,
            behavior: "smooth"
        });
    }

    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: "smooth"
    });
}