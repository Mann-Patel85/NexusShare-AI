document.addEventListener("DOMContentLoaded", () => {
    fetchFiles();
});

function fetchFiles() {
    fetch("/files")
        .then(response => response.json())
        .then(data => {
            const fileList = document.getElementById("file-list");
            const files = data.available_files;

            if (files.length > 0) {
                files.forEach(file => {
                    const li = document.createElement("li");
                    li.textContent = `📄 ${file}`;
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