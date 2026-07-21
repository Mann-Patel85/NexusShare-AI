document.addEventListener("DOMContentLoaded", () => {
    fetchFiles();
});

function fetchFiles() {
    fetch("/files")
        .then(response => response.json())
        .then(data => {
            const fileList = document.getElementById("file-list");
            
            // Clear any old content first
            fileList.innerHTML = ""; 
            
            // Safely check if available_files exists AND actually has items
            if (data.available_files && data.available_files.length > 0) {
                data.available_files.forEach(file => {
                    const li = document.createElement("li");
                    li.textContent = `📄 ${file}`;
                    fileList.appendChild(li);
                });
            } else {
                // If it doesn't exist (e.g., folder just created or is empty)
                fileList.innerHTML = "<li>No files available in the shared folder.</li>";
            }
        })
        .catch(error => {
            console.error("Error fetching files:", error);
            document.getElementById("file-list").innerHTML = "<li>Error connecting to server.</li>";
        });
}