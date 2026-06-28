import { postFormToApi } from "./api.js";

const attachedImages = new Map();
let nextFormId = 1;

function createForm(initialData = {}, imageFile = null) {
    const formsContainer = document.getElementById("formsContainer");
    const formTemplate = document.getElementById("thingFormTemplate");
    const fragment = formTemplate.content.cloneNode(true);
    const form = fragment.querySelector("form");
    const formId = `thing-form-${nextFormId++}`;
    form.dataset.formId = formId;

    const thingNameInput = form.querySelector("input[name=thingName]");
    const fromThingInput = form.querySelector("input[name=fromThingName]");
    const fileInput = form.querySelector("input[name=thingImage]");
    const preview = form.querySelector(".imagePreview");
    const message = form.querySelector(".formMessage");

    thingNameInput.value = initialData.thingName || "";
    fromThingInput.value = initialData.fromThingName || "";

    function updatePreview(file) {
        if (!file) {
            attachedImages.delete(formId);
            preview.src = "";
            preview.style.display = "none";
            return;
        }
        attachedImages.set(formId, file);
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
    }

    fileInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        updatePreview(file);
    });

    if (imageFile) {
        updatePreview(imageFile);
    } else {
        preview.style.display = "none";
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await submitThingForm(form);
    });

    formsContainer.appendChild(form);
    return form;
}

async function submitThingForm(form) {
    const formId = form.dataset.formId;
    const message = form.querySelector(".formMessage");
    message.textContent = "";

    const formData = new FormData(form);
    if (attachedImages.has(formId)) {
        formData.set("thingImage", attachedImages.get(formId));
    }

    const thingName = formData.get("thingName").trim();
    if (!thingName) {
        message.textContent = "Please enter a thing name.";
        message.classList.remove("success-message");
        message.classList.add("error-message");
        return;
    }

    const result = await postFormToApi(formData, "/api/thing");
    if (result) {
        message.textContent = `Successfully added ${thingName}.`;
        message.classList.remove("error-message");
        message.classList.add("success-message");
    } else {
        message.textContent = "Error submitting this thing.";
        message.classList.remove("success-message");
        message.classList.add("error-message");
    }
}

function duplicateCurrentForm() {
    const formsContainer = document.getElementById("formsContainer");
    const lastForm = formsContainer.querySelector("form:last-of-type");
    if (!lastForm) {
        createForm();
        return;
    }

    const values = {
        thingName: lastForm.querySelector("input[name=thingName]").value,
        fromThingName: lastForm.querySelector("input[name=fromThingName]").value,
    };
    const formId = lastForm.dataset.formId;
    const imageFile = attachedImages.get(formId) || null;
    createForm(values, imageFile);
}

function initialize() {
    const bulkImageUpload = document.getElementById("bulkImageUpload");
    const duplicateFormButton = document.getElementById("duplicateFormButton");

    bulkImageUpload.addEventListener("change", (event) => {
        const files = Array.from(event.target.files || []);
        files.forEach((file) => createForm({}, file));
        event.target.value = "";
    });

    duplicateFormButton.addEventListener("click", duplicateCurrentForm);
    createForm();
}

document.addEventListener("DOMContentLoaded", initialize);
