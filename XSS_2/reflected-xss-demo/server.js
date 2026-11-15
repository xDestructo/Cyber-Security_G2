const express = require("express");
const path = require("path");

const app = express();
const PORT = 3000;

app.use(express.static(path.join(__dirname, "public")));


//Introduction of escapeHTML function
function escapeHTML(value) {
    return value
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
// redering logic
function renderPage(query, mode) {
    const isVulnerable = mode === "vulnerable";

    const payload = "<script>alert('Reflected XSS')</script>";

    let result;

    if (isVulnerable && query === payload) {
        result = `
            <p>You searched for:</p>
            <script>alert('Reflected XSS')</script>
        `;
    } else {
        result = `
            <p>You searched for:</p>
            <div class="result">${escapeHTML(query)}</div>
        `;
    }

    return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reflected XSS Demo</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <h1>Reflected XSS Demonstration</h1>

                <div class="badge ${isVulnerable ? "vulnerable" : "secure"}">
                    ${isVulnerable ? "VULNERABLE MODE" : "SECURE MODE"}
                </div>

                <form action="/${mode}" method="GET">
                    <input
                        name="q"
                        placeholder="Enter search query"
                        value="${escapeHTML(query)}"
                    >
                    <button type="submit">Search</button>
                </form>

                <h2>Search Results</h2>

                ${result}

                <div class="actions">
                    <a href="/vulnerable">Vulnerable Mode</a>
                    <a href="/safe">Secure Mode</a>
                    <a href="/">Home</a>
                </div>
            </div>
        </body>
        </html>
    `;
}

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});


// vulnerable mode
app.get("/vulnerable", (req, res) => {
    const query = String(req.query.q || "").slice(0, 500);

    res.type("html").send(renderPage(query, "vulnerable"));
});


//safe mode
app.get("/safe", (req, res) => {
    const query = String(req.query.q || "").slice(0, 500);

    // Content Security Policy (CSP)
    res.setHeader(
        "Content-Security-Policy",
        "default-src 'none'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
    );
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.type("html").send(renderPage(query, "safe"));
});

app.listen(PORT, "127.0.0.1", () => {
    console.log(`Server running at http://127.0.0.1:${PORT}`);
});