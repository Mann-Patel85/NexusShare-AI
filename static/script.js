document.addEventListener("DOMContentLoaded", () => {
    fetchFiles();
});

// --- 1. FETCH AND DISPLAY FILES ---
function fetchFiles() {
    fetch("/files")
        .then(response => response.json())
        .then(data => {
            const fileList = document.getElementById("file-list");
            fileList.innerHTML = ""; 
            
            if (data.available_files && data.available_files.length > 0) {
                data.available_files.forEach(file => {
                    const li = document.createElement("li");
                    const link = document.createElement("a");
                    link.href = `/download/${file}`;
                    link.download = file; 
                    link.textContent = `📄 ${file}`;
                    link.style.color = "var(--text-primary)";
                    link.style.textDecoration = "none";
                    
                    li.appendChild(link);
                    fileList.appendChild(li);
                });
            } else {
                fileList.innerHTML = "<li>No files available in the shared folder.</li>";
            }
        })
        .catch(error => {
            console.error("Error fetching files:", error);
            document.getElementById("file-list").innerHTML = "<li>Error connecting to server.</li>";
        });
}

// --- 2. DRAG AND DROP UPLOAD LOGIC ---
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const statusText = document.getElementById("upload-status");

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleUpload(files[0]);
    }
});

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        handleUpload(this.files[0]);
    }
});

function handleUpload(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    statusText.textContent = `Uploading ${file.name}...`;

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        statusText.textContent = `Success: ${data.filename} uploaded!`;
        fetchFiles(); 
    })
    .catch(error => {
        console.error("Upload failed:", error);
        statusText.textContent = "Error uploading file.";
    });
}