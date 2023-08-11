let uploadButton = document.getElementById("upload-button");
let container = document.querySelector(".container");
let error = document.getElementById("error");
let imageDisplayRight = document.getElementById("image-display-right");

const fileHandler = (file, name, type) => {
  if (type.split("/")[0] !== "image") {
    // File Type Error
    error.innerText = "Please upload an image file";
    return false;
  }
  error.innerText = "";
  let reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onloadend = () => {
    // Image and file name
    let imageContainer = document.createElement("figure");
    let img = document.createElement("img");
    img.src = reader.result;
    imageContainer.appendChild(img);
    imageContainer.innerHTML += `<figcaption>${name}</figcaption>`;
    imageDisplayRight.appendChild(imageContainer);
  };
};

function output_callback(response) {
  let outputContainer = document.getElementById("outputstatic");
  let logContainer = document.createElement("div");

  // Clear previous content
  outputContainer.innerHTML = "";

  // Display result and extracted text
  outputContainer.innerHTML += `<p>Result: ${response.result}</p>`;
  outputContainer.innerHTML += `<p>Extracted Text: ${response.extracted_text}</p>`;

  // Display log messages
  logContainer.innerHTML = "<h3>Log Messages:</h3>";
  response.log_messages.forEach((log) => {
    let logItem = document.createElement("p");
    logItem.innerText = log;
    logContainer.appendChild(logItem);
  });
  outputContainer.appendChild(logContainer);
}

// Upload Button
uploadButton.addEventListener("change", () => {
  imageDisplayRight.innerHTML = "";
  Array.from(uploadButton.files).forEach((file) => {
    fileHandler(file, file.name, file.type);
  });
});

container.addEventListener(
  "dragenter",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.add("active");
  },
  false
);

container.addEventListener(
  "dragleave",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.remove("active");
  },
  false
);

container.addEventListener(
  "dragover",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.add("active");
  },
  false
);

container.addEventListener(
  "drop",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.remove("active");
    let draggedData = e.dataTransfer;
    let files = draggedData.files;
    imageDisplayRight.innerHTML = "";
    Array.from(files).forEach((file) => {
      fileHandler(file, file.name, file.type);
    });
  },
  false
);

function showDetails(itemNumber) {
  const detailsElement = document.getElementById(`details${itemNumber}`);
  detailsElement.classList.toggle("show");
}

window.addEventListener('DOMContentLoaded', () => {
  error.innerText = "";
});
