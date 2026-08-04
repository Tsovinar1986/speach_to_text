const tabFile = document.getElementById("tabFile");
const tabLink = document.getElementById("tabLink");
const filePane = document.getElementById("filePane");
const linkPane = document.getElementById("linkPane");
const urlInput = document.getElementById("urlInput");

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const clearFile = document.getElementById("clearFile");
const langSelect = document.getElementById("langSelect");
const submitBtn = document.getElementById("submitBtn");
const submitLabel = document.getElementById("submitLabel");
const progress = document.getElementById("progress");
const errorBox = document.getElementById("errorBox");
const resultBox = document.getElementById("resultBox");
const resultText = document.getElementById("resultText");
const detectedLang = document.getElementById("detectedLang");
const copyBtn = document.getElementById("copyBtn");

let selectedFile = null;
let mode = "file"; // "file" | "link"

function updateSubmitState() {
  const hasInput = mode === "file" ? !!selectedFile : urlInput.value.trim().length > 0;
  submitBtn.disabled = !hasInput;
}

function setMode(newMode) {
  mode = newMode;
  tabFile.classList.toggle("active", mode === "file");
  tabLink.classList.toggle("active", mode === "link");
  filePane.classList.toggle("hidden", mode !== "file");
  linkPane.classList.toggle("hidden", mode !== "link");
  hideError();
  resultBox.classList.add("hidden");
  updateSubmitState();
}

tabFile.addEventListener("click", () => setMode("file"));
tabLink.addEventListener("click", () => setMode("link"));
urlInput.addEventListener("input", updateSubmitState);

function setFile(file) {
  selectedFile = file;
  if (file) {
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
  } else {
    fileInfo.classList.add("hidden");
  }
  hideError();
  resultBox.classList.add("hidden");
  updateSubmitState();
}

fileInput.addEventListener("change", () => {
  setFile(fileInput.files[0] || null);
});

clearFile.addEventListener("click", (e) => {
  e.preventDefault();
  fileInput.value = "";
  setFile(null);
});

["dragenter", "dragover"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    setFile(file);
  }
});

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.classList.add("hidden");
  errorBox.textContent = "";
}

function setLoading(isLoading) {
  updateSubmitState();
  if (isLoading) submitBtn.disabled = true;
  progress.classList.toggle("hidden", !isLoading);
  submitLabel.textContent = isLoading ? "Մշակվում է..." : "Ստանալ տեքստը";
}

submitBtn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (mode === "file" && !selectedFile) return;
  if (mode === "link" && !url) return;

  hideError();
  resultBox.classList.add("hidden");
  setLoading(true);

  const formData = new FormData();
  if (mode === "file") {
    formData.append("file", selectedFile);
  } else {
    formData.append("url", url);
  }

  const params = new URLSearchParams();
  if (langSelect.value) {
    params.set("language", langSelect.value);
  }

  try {
    const response = await fetch(`/api/speech-to-text?${params.toString()}`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.detail || `Սխալ (${response.status})`);
    }

    const data = await response.json();
    resultText.value = data.text || "";
    detectedLang.textContent = data.language ? data.language.toUpperCase() : "";
    resultBox.classList.remove("hidden");
  } catch (err) {
    showError(err.message || "Անհայտ սխալ տեղի ունեցավ։");
  } finally {
    setLoading(false);
  }
});

copyBtn.addEventListener("click", async () => {
  if (!resultText.value) return;
  try {
    await navigator.clipboard.writeText(resultText.value);
    const original = copyBtn.textContent;
    copyBtn.textContent = "Պատճենվեց ✓";
    setTimeout(() => (copyBtn.textContent = original), 1500);
  } catch {
    resultText.select();
    document.execCommand("copy");
  }
});
