import { sendFormToApi } from "./api.js";
import { addSearchability } from "./search.js";
import { addFromThingInput, removeEmptyFromThingNames, submitVoteForm } from "./form-helpers.js";

document.addEventListener('DOMContentLoaded', () => {
    const attachedImages = new Map();
    let nextFormId = 1;
    initialize()

    function populateFromThingInputs(form, values = []) {
        const inputs = Array.from(form.querySelectorAll("input[name='fromThingNames']"));
        inputs.forEach((input, index) => {
            input.value = values[index] || "";
        });

        values.slice(inputs.length).forEach((value) => {
            const lastInput = form.querySelector("input[name='fromThingNames']:last-of-type");
            if (!lastInput) {
                return;
            }
            const newInput = addFromThingInput(lastInput);
            newInput.value = value;
        });
    }

    function createForm(initialData = {}, imageFile = null, firstTime = false) {
        const formsContainer = document.getElementById("formsContainer");
        let form = document.getElementById("addForm")
        if (!firstTime) {
            form = form.cloneNode(true);
        }
        const fromThingInput = form.querySelector("input[name='fromThingNames']");
        const addFromThingButton = form.querySelector(".add-from-thing-button");
        const fileInput = form.querySelector("input[name=thingImage]");
        const formId = `thing-form-${nextFormId++}`;
        form.dataset.formId = formId;

        const thingNameInput = form.querySelector("input[name=thingName]");
        
        const preview = form.querySelector(".imagePreview");
        const message = form.querySelector(".formMessage");

        thingNameInput.value = initialData.thingName || "";
        const initialFromThingNames = Array.isArray(initialData.fromThingNames)
            ? initialData.fromThingNames
            : initialData.fromThingName
                ? [initialData.fromThingName]
                : [];
        populateFromThingInputs(form, initialFromThingNames);

        function updatePreview(file) {
            if (!file) {
                attachedImages.delete(formId);
                preview.src = "";
                preview.style.display = "none";

                const dt = new DataTransfer();
                fileInput.files = dt.files;

                return;
            }

            attachedImages.set(formId, file);

            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;

            preview.src = URL.createObjectURL(file);
        }

        if (imageFile) {
            updatePreview(imageFile);
        } else {
        }

        form.addEventListener("submit", submitVoteForm);

        if (addFromThingButton && fromThingInput) {
            addFromThingButton.addEventListener("click", () => addFromThingInput(fromThingInput));
        }

        fileInput.addEventListener("change", (event) => {
            const file = event.target.files[0];
            updatePreview(file);
        });

        addSearchability(form);
        formsContainer.appendChild(form);
        return form;
    }

    async function submitThingForm(form) {
        const formId = form.dataset.formId;
        const message = form.querySelector(".formMessage");
        message.textContent = "";

        const formData = new FormData(form);
        removeEmptyFromThingNames(formData);
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

        const result = await sendFormToApi(formData, "/api/thing", "POST");
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
            fromThingNames: Array.from(lastForm.querySelectorAll("input[name='fromThingNames']")).map((input) => input.value),
        };
        const formId = lastForm.dataset.formId;
        const imageFile = attachedImages.get(formId) || null;
        createForm(values, imageFile);
    }

    function initialize() {
        const bulkImageUpload = document.getElementById("bulkImageUpload");
        const duplicateFormButton = document.getElementById("duplicateFormButton");
        const form = document.getElementById("addForm");

        bulkImageUpload.addEventListener("change", (event) => {
            const files = Array.from(event.target.files || []);
            files.forEach((file) => createForm({}, file));
            event.target.value = "";
        });

        duplicateFormButton.addEventListener("click", duplicateCurrentForm);
        createForm({}, null, true);
    }
});
