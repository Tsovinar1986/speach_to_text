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

function setFile(file) {
  selectedFile = file;
  if (file) {
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    submitBtn.disabled = false;
  } else {
    fileInfo.classList.add("hidden");
    submitBtn.disabled = true;
  }
  hideError();
  resultBox.classList.add("hidden");
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
  submitBtn.disabled = isLoading || !selectedFile;
  progress.classList.toggle("hidden", !isLoading);
  submitLabel.textContent = isLoading ? "Մշակվում է..." : "Ստանալ տեքստը";
}

submitBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  hideError();
  resultBox.classList.add("hidden");
  setLoading(true);

  const formData = new FormData();
  formData.append("file", selectedFile);

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

const ttsInput = document.getElementById("ttsInput");
const ttsBtn = document.getElementById("ttsBtn");
const ttsProgress = document.getElementById("ttsProgress");
const ttsErrorBox = document.getElementById("ttsErrorBox");
const ttsResult = document.getElementById("ttsResult");
const ttsAudio = document.getElementById("ttsAudio");
const ttsDownload = document.getElementById("ttsDownload");

let ttsAudioUrl = null;

ttsBtn.addEventListener("click", async () => {
  const text = ttsInput.value.trim();
  if (!text) return;

  ttsErrorBox.classList.add("hidden");
  ttsResult.classList.add("hidden");
  ttsProgress.classList.remove("hidden");
  ttsBtn.disabled = true;

  try {
    const response = await fetch("/api/text-to-speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.detail || `Սխալ (${response.status})`);
    }

    const blob = await response.blob();
    if (ttsAudioUrl) URL.revokeObjectURL(ttsAudioUrl);
    ttsAudioUrl = URL.createObjectURL(blob);
    ttsAudio.src = ttsAudioUrl;
    ttsDownload.href = ttsAudioUrl;
    ttsResult.classList.remove("hidden");
  } catch (err) {
    ttsErrorBox.textContent = err.message || "Անհայտ սխալ տեղի ունեցավ։";
    ttsErrorBox.classList.remove("hidden");
  } finally {
    ttsProgress.classList.add("hidden");
    ttsBtn.disabled = false;
  }
});
