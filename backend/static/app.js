const methodField = document.getElementById("method");
const endpointField = document.getElementById("endpoint");
const reqBodyField = document.getElementById("request_body");
const responseField = document.getElementById("response");
const statusField = document.getElementById("status");
const sendButton = document.getElementById("sendButton");

function buildQuery(endpoint, text) {
    if (!text) {
        return endpoint;
    }

    const paramsObject = JSON.parse(text);
    const params = new URLSearchParams();

    Object.entries(paramsObject).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            params.append(key, value);
        }
    });

    const query = params.toString();
    if (!query) {
        return endpoint;
    }

    return endpoint + (endpoint.includes("?") ? "&" : "?") + query;
}

async function sendRequest() {
    const method = methodField.value;
    let endpoint = endpointField.value.trim();
    const bodyText = reqBodyField.value.trim();

    if (!endpoint.startsWith("/")) {
        responseField.value =
            "Endpoint должен начинаться с /. Например: /get_article";
        return;
    }

    const options = { method };

    try {
        if (method === "GET" || method === "DELETE") {
            endpoint = buildQuery(endpoint, bodyText);
        } else {
            if (bodyText) {
                JSON.parse(bodyText);
            }
            options.headers = {
                "Content-Type": "application/json; charset=utf-8"
            };
            options.body = bodyText || "{}";
        }
    } catch (error) {
        statusField.textContent = "Некорректный JSON";
        responseField.value = String(error);
        return;
    }

    statusField.textContent = "Sending request...";
    responseField.value = "";
    const startedAt = performance.now();

    try {
        const response = await fetch(endpoint, options);
        const elapsed = Math.round(performance.now() - startedAt);
        const text = await response.text();

        statusField.textContent =
            `Status: ${response.status} ${response.statusText} | ${elapsed} ms`;

        try {
            responseField.value = JSON.stringify(JSON.parse(text), null, 2);
        } catch {
            responseField.value = text;
        }
    } catch (error) {
        statusField.textContent = "Request failed";
        responseField.value = String(error);
    }
}

sendButton.addEventListener("click", sendRequest);
