const methodField = document.getElementById("method");
const endpointField = document.getElementById("endpoint");
// const paramsField = document.getElementById("params");
const reqBodyField = document.getElementById("request_body");
const responseField = document.getElementById("response");
const statusField = document.getElementById("status");
const sendButton = document.getElementById("sendButton");

async function sendRequest() {
    const method = methodField.value;
    let endpoint = endpointField.value.trim();
    // const params = paramsField.value.trim().replace(/^\?/, "");
    if (!endpoint.startsWith("/")) {
        responseField.value = "Endpoint должен начинаться с /. Например: /get_some_data";
        return;
    }
    
    statusField.textContent = "Sending request...";
    responseField.value = "";
    
    // const separator = endpoint.includes("?") ? "&" : "?";
    // let requestUrl = params ? `${endpoint}${separator}${params}` : endpoint;
    
    const options = { method: method };
    
    console.log('method: ', method)
    if (method !== "GET") {
        options.headers = {
            "Content-Type": "application/json;charset=utf-8",
        };
        options.body = reqBodyField.value.trim();
    } else {
        console.log(reqBodyField.value.trim())
        try {
            const propObj = JSON.parse(reqBodyField.value.trim());
            console.log('propObj: ', propObj);
            const propEntries = Object.entries(propObj)
            console.log('propEntries: ', propEntries);
            const mapObj = propEntries.map(([key, value]) => {
                return `${key}=${value}`;
        })
        console.log("strArr:", mapObj.join('&'));
        endpoint = endpoint +'?' + mapObj.join('&');
        }
        catch (e){
            console.log(e)
        }
    }

    const startedAt = performance.now();

    try {
        console.log(endpoint, options);
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
