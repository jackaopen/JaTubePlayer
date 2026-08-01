const DEFAULT_PORT = 5000;
const MIN_PORT = 1024;
const MAX_PORT = 65535;

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#port-form");
  const portInput = document.querySelector("#port");
  const status = document.querySelector("#status");

  function showStatus(message, isError = false) {
    status.textContent = message;
    status.style.color = isError ? "#ff6b6b" : "#5bd890";
  }

  async function loadPort() {
    try {
      const { port = DEFAULT_PORT } = await chrome.storage.local.get("port");
      portInput.value = port;
    } catch (error) {
      showStatus(`Could not load the port: ${error.message}`, true);
    }
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    
    const port = portInput.valueAsNumber;

    if (!Number.isInteger(port) || port < MIN_PORT || port > MAX_PORT) {
      showStatus(`Enter a whole number from ${MIN_PORT} to ${MAX_PORT}.`, true);
      portInput.focus();
      return;
    }

    try {
      await chrome.storage.local.set({ port });
      showStatus(`Port ${port} saved.`);
    } catch (error) {
      showStatus(`Could not save the port: ${error.message}`, true);
    }
  });

  loadPort();
});
