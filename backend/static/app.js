const methodField = document.getElementById("method");
const endpointField = document.getElementById("endpoint");
const paramsField = document.getElementById("params");
const responseField = document.getElementById("response");
const statusField = document.getElementById("status");
const sendButton = document.getElementById("sendButton");

async function sendRequest() {
    const method = methodField.value;
    const endpoint = endpointField.value.trim();
    const params = paramsField.value.trim().replace(/^\?/, "");

    if (!endpoint.startsWith("/")) {
        responseField.value = "Endpoint должен начинаться с /. Например: /get_some_data";
        return;
    }

    statusField.textContent = "Sending request...";
    responseField.value = "";

    const separator = endpoint.includes("?") ? "&" : "?";
    const requestUrl = params ? `${endpoint}${separator}${params}` : endpoint;

    const options = { method };

    if (method === "POST") {
        options.headers = {
            "Content-Type": "application/json"
        };
        options.body = JSON.stringify({ hello: "world" });
    }

    const startedAt = performance.now();

    try {
        const response = await fetch(requestUrl, options);
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
