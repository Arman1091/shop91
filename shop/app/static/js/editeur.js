document.addEventListener('DOMContentLoaded', function () {
    updateOutput();
    makeDraggableAndResizable(document.getElementById('qr-preview'));
    makeDraggableAndResizable(document.getElementById('logo-preview'));
    document.querySelectorAll('.preview-text').forEach(el => {
        makeTextDraggable(el);
    });

    document.getElementById('customize-form').addEventListener('submit', function (e) {
        updateFormFields();
    });


});

function addNewInput() {
    let inputList = document.getElementById("input-list");
    let container = document.createElement("div");
    container.classList.add("input-container");
    container.innerHTML = `
        <div class="input-row">
            <input class="lign_input" type="text" name="texte[]" placeholder="Tapez ici..." value="Premier texte" oninput="updateOutput()">
            <input class="lign_input_hiden d-none" name="hidden_texte[]" value="Premier texte" style="position: absolute; font-size: 16px; color: #000000; left: 0px; top: 0px;">
            <button class="delete-btn" type="button" onclick="this.closest('.input-container').remove(); updateOutput()">
                <i class="bi bi-trash3 delete-icon"></i>
            </button>
        </div>
        <div class="controls">
            <input class="font-input" type="number" name="taille_police[]" value="16" min="10" max="50" oninput="updateStyle(this, 'fontSize', 'px')">
            <button class="toggle-btn" type="button" onclick="toggleStyle(this, 'fontWeight', 'bold', 'normal')">B</button>
            <button class="toggle-btn" type="button" onclick="toggleStyle(this, 'fontStyle', 'italic', 'normal')">I</button>
            <button class="toggle-btn" type="button" onclick="toggleStyle(this, 'textDecoration', 'underline', 'none')">U</button>
            <button class="toggle-btn align-btn" type="button" onclick="setAlignment(this, 'start')"><i class="bi bi-justify-left"></i></button>
            <button class="toggle-btn align-btn" type="button" onclick="setAlignment(this, 'center')"><i class="bi bi-justify"></i></button>
            <button class="toggle-btn align-btn" type="button" onclick="setAlignment(this, 'end')"><i class="bi bi-justify-right"></i></button>
        </div>
    `;
    inputList.appendChild(container);
    updateOutput();

    let newInput = container.querySelector(".lign_input");
    let newControls = container.querySelector(".controls");
    newInput.addEventListener("focus", function () {
        newControls.style.display = "flex";
        this.setAttribute("data-active", "true");
    });
    newInput.addEventListener("blur", function () {
        setTimeout(() => {
            if (!newControls.matches(":hover")) {
                newControls.style.display = "none";
                this.removeAttribute("data-active");
            }
        }, 200);
    });
}

function toggleStyle(button, styleProp, valueOn, valueOff) {
    let container = button.closest('.input-container');
    let hiddenInput = container.querySelector('.lign_input_hiden');
    let currentStyle = hiddenInput.style[styleProp] || getComputedStyle(hiddenInput)[styleProp];
    hiddenInput.style[styleProp] = (currentStyle === valueOn) ? valueOff : valueOn;
    button.classList.toggle("active");
    updateOutput();
}

function updateStyle(input, styleProp, unit) {
    let container = input.closest('.input-container');
    let hiddenInput = container.querySelector('.lign_input_hiden');
    hiddenInput.style[styleProp] = input.value + unit;
    updateOutput();
}

function setAlignment(button, alignValue) {
    let container = button.closest('.input-container');
    let hiddenInput = container.querySelector('.lign_input_hiden');
    hiddenInput.style.textAlign = alignValue;
    button.parentElement.querySelectorAll(".align-btn").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    updateOutput();
}

function updateOutput() {
    let outputDiv = document.getElementById("output");
    let productImg = document.getElementById("logo-preview");
    let qrPreview = document.getElementById("qr-preview");
    outputDiv.innerHTML = "";

    if (productImg) {
        let logo = productImg.cloneNode(true);
        logo.id = "logo-preview";
        outputDiv.appendChild(logo);
    }

    if (qrPreview) {
        let qrClone = qrPreview.cloneNode(true);
        qrClone.id = "qr-preview";
        outputDiv.appendChild(qrClone);
    }

    document.querySelectorAll(".input-container").forEach((container, index) => {
        let input = container.querySelector(".lign_input");
        let hiddenInput = container.querySelector('.lign_input_hiden');
        let textElement = document.createElement("div");

        hiddenInput.value = input.value;
        textElement.textContent = input.value;
        textElement.style.cssText = hiddenInput.style.cssText;

        let containerWidth = outputDiv.offsetWidth;
        document.body.appendChild(textElement);
        let textWidth = textElement.offsetWidth;
        document.body.removeChild(textElement);

        let align = hiddenInput.style.textAlign || "left";
        let positionX = parseInt(hiddenInput.style.left) || 0;
        if (align === "center") {
            positionX = (containerWidth - textWidth) / 2;
        } else if (align === "end") {
            positionX = containerWidth - textWidth;
        }
        textElement.style.left = `${positionX}px`;
        hiddenInput.style.left = `${positionX}px`;

        textElement.classList.add("output-text", "draggable", "preview-text");
        textElement.id = "text-" + index;
        outputDiv.appendChild(textElement);
    });

    makeDraggableAndResizable(document.getElementById('qr-preview'));
    makeDraggableAndResizable(document.getElementById('logo-preview'));
    document.querySelectorAll('.preview-text').forEach(el => {
        makeTextDraggable(el);
    });
}

function updateFormFields() {
    let logoPreview = document.getElementById('logo-preview');
    let qrPreview = document.getElementById('qr-preview');

    document.getElementById('logo-width').value = parseInt(logoPreview.style.width) || 50;
    document.getElementById('logo-height').value = parseInt(logoPreview.style.height) || 50;
    document.getElementById('logo-position-x').value = parseInt(logoPreview.style.left) || 100;
    document.getElementById('logo-position-y').value = parseInt(logoPreview.style.top) || 30;

    document.getElementById('qrCode-width').value = parseInt(qrPreview.style.width) || 50;
    document.getElementById('qrCode-height').value = parseInt(qrPreview.style.height) || 50;
    document.getElementById('qrCode-position-x').value = parseInt(qrPreview.style.left) || 100;
    document.getElementById('qrCode-position-y').value = parseInt(qrPreview.style.top) || 30;

    document.querySelectorAll('.input-container').forEach(container => {
        let input = container.querySelector('.lign_input');
        let hiddenInput = container.querySelector('.lign_input_hiden');
        hiddenInput.value = input.value;
    });
}

function updateQR() {
    const qrUrl = document.getElementById('qr-url').value;
    if (qrUrl) {
        const qrApi = `https://api.qrserver.com/v1/create-qr-code/?size=50x50&data=${encodeURIComponent(qrUrl)}`;
        document.getElementById('qr-preview').style.backgroundImage = `url(${qrApi})`;
        document.getElementById('qr-preview').style.display = 'block';
    } else {
        document.getElementById('qr-preview').style.backgroundImage = 'none';
        document.getElementById('qr-preview').style.display = 'none';
    }
}

function makeDraggableAndResizable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    let resizing = false, startX, startY, startWidth, startHeight;
    const handle = element.querySelector('.resize-handle');

    element.addEventListener('mousedown', startDrag, false);
    element.addEventListener('touchstart', startDrag, false);

    function startDrag(e) {
        e.preventDefault();
        if (e.type === 'mousedown') {
            pos3 = e.clientX;
            pos4 = e.clientY;
        } else if (e.type === 'touchstart') {
            pos3 = e.touches[0].clientX;
            pos4 = e.touches[0].clientY;
        }

        if (e.target === handle) {
            resizing = true;
            if (e.type === 'mousedown') {
                startX = e.clientX;
                startY = e.clientY;
            } else if (e.type === 'touchstart') {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            }
            startWidth = parseInt(element.style.width || 40);
            startHeight = parseInt(element.style.height || 40);
        } else {
            document.onmousemove = elementDrag;
            document.onmouseup = closeDragElement;
            document.ontouchmove = elementDrag;
            document.ontouchend = closeDragElement;
        }
    }

    function elementDrag(e) {
        e.preventDefault();
        if (resizing) {
            let newWidth, newHeight;
            if (e.type === 'mousemove') {
                newWidth = startWidth + (e.clientX - startX);
                newHeight = startHeight + (e.clientY - startY);
            } else if (e.type === 'touchmove') {
                newWidth = startWidth + (e.touches[0].clientX - startX);
                newHeight = startHeight + (e.touches[0].clientY - startY);
            }
            newWidth = Math.max(20, Math.min(100, newWidth));
            newHeight = Math.max(20, Math.min(100, newHeight));
            element.style.width = newWidth + 'px';
            element.style.height = newHeight + 'px';
        } else {
            let newPosX, newPosY;
            if (e.type === 'mousemove') {
                newPosX = pos3 - e.clientX;
                newPosY = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
            } else if (e.type === 'touchmove') {
                newPosX = pos3 - e.touches[0].clientX;
                newPosY = pos4 - e.touches[0].clientY;
                pos3 = e.touches[0].clientX;
                pos4 = e.touches[0].clientY;
            }
            element.style.top = (element.offsetTop - newPosY) + "px";
            element.style.left = (element.offsetLeft - newPosX) + "px";

            const preview = document.getElementById('output');
            const rect = preview.getBoundingClientRect();
            const elRect = element.getBoundingClientRect();

            if (elRect.top < rect.top) element.style.top = "0px";
            if (elRect.left < rect.left) element.style.left = "0px";
            if (elRect.bottom > rect.bottom) element.style.top = (preview.offsetHeight - elRect.height) + "px";
            if (elRect.right > rect.right) element.style.left = (preview.offsetWidth - elRect.width) + "px";
        }
    }

    function closeDragElement() {
        document.onmousemove = null;
        document.onmouseup = null;
        document.ontouchmove = null;
        document.ontouchend = null;
        resizing = false;
    }
}

function makeTextDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    element.addEventListener('mousedown', dragMouseDown, false);
    element.addEventListener('touchstart', dragMouseDown, { passive: false });

    function dragMouseDown(e) {
        e.preventDefault();
        if (e.type === 'mousedown') {
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        } else if (e.type === 'touchstart') {
            pos3 = e.touches[0].clientX;
            pos4 = e.touches[0].clientY;
            document.ontouchend = closeDragElement;
            document.ontouchmove = elementDrag;
        }
    }

    function elementDrag(e) {
        e.preventDefault();
        let newPosX = pos3 - (e.type === 'mousemove' ? e.clientX : e.touches[0].clientX);
        let newPosY = pos4 - (e.type === 'mousemove' ? e.clientY : e.touches[0].clientY);
        pos3 = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
        pos4 = e.type === 'mousemove' ? e.clientY : e.touches[0].clientY;

        let newLeft = element.offsetLeft - newPosX;
        let newTop = element.offsetTop - newPosY;

        const preview = document.getElementById('output');
        const rect = preview.getBoundingClientRect();
        const elRect = element.getBoundingClientRect();

        newLeft = Math.max(0, Math.min(newLeft, preview.offsetWidth - elRect.width));
        newTop = Math.max(0, Math.min(newTop, preview.offsetHeight - elRect.height));

        element.style.left = newLeft + "px";
        element.style.top = newTop + "px";

        let container = document.querySelector(`[data-line-id="${element.id.split('-')[1]}"]`);
        if (container) {
            let hiddenInput = container.querySelector('.lign_input_hiden');
            hiddenInput.style.left = newLeft + "px";
            hiddenInput.style.top = newTop + "px";
        }
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
        document.ontouchend = null;
        document.ontouchmove = null;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const logoModal = document.getElementById("logo-modal");
    const logoOpenBtn = document.getElementById("add_logo");
    const logoCloseBtn = document.querySelector(".close-modal-logo");
    const logoPreview = document.getElementById("logo-preview");
    const fileInput = document.getElementById("upload-logo");

    logoOpenBtn.addEventListener("click", () => logoModal.style.display = "flex");
    logoCloseBtn.addEventListener("click", () => logoModal.style.display = "none");

    document.querySelectorAll(".logo-option").forEach(img => {
        img.addEventListener("click", function () {
            logoPreview.style.backgroundImage = `url(${img.src})`;
            logoModal.style.display = "none";
        });
    });

    fileInput.addEventListener("change", function (event) {
        let file = event.target.files[0];
        if (file) {
            let reader = new FileReader();
            reader.onload = function (e) {
                logoPreview.style.backgroundImage = `url(${e.target.result})`;
                logoModal.style.display = "none";
            };
            reader.readAsDataURL(file);
        }
    });

    const materialModal = document.getElementById("material-modal");
    const materialOpenBtn = document.getElementById("select_materiel");
    const materialCloseBtn = document.querySelector(".close-modal-materiel");

    materialOpenBtn.addEventListener("click", () => materialModal.style.display = "flex");
    materialCloseBtn.addEventListener("click", () => materialModal.style.display = "none");

    document.querySelectorAll(".select-materiel-plaque").forEach(item => {
        item.addEventListener("click", function () {
            document.getElementById("material-id").value = this.dataset.materialId;
            materialModal.style.display = "none";
        });
    });

    const colorModal = document.getElementById("color-modal");
    const colorOpenBtn = document.getElementById("select_color");
    const colorCloseBtn = document.querySelector(".close-modal-color");

    colorOpenBtn.addEventListener("click", () => colorModal.style.display = "flex");
    colorCloseBtn.addEventListener("click", () => colorModal.style.display = "none");

    document.querySelectorAll(".color-option").forEach(color => {
        color.addEventListener("click", function () {
            document.getElementById("plaque-color-id").value = this.dataset.colorId;
            colorModal.style.display = "none";
        });
    });
});
