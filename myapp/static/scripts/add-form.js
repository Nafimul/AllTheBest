"use strict";

document.addEventListener("DOMContentLoaded", function() {
    const form = document.forms.namedItem("addForm");
    const successMessage = document.getElementById("successMessage");
    const thingImage = document.getElementById("thingImage");
    const imagePreview = document.getElementById("imagePreview");

    function previewImage(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function() {
                imagePreview.src = reader.result;
            }
            reader.readAsDataURL(file);
        } else {
            imagePreview.src = "";
        }
    }
    thingImage.addEventListener("change", previewImage);

    async function submit(e) {
        e.preventDefault();
        let response = await postFormToApi(new FormData(form), "/api/thing");
        if (response.ok) {
            let responseJson = await response.json()
            successMessage.innerText = responseJson["message"]
        }
        else
            successMessage.innerText = "Error adding thing";
    }

    async function postFormToApi(formData, url) {
        try {
            let formData = new FormData(form);
            const response = await fetch(url,
                                        {
                                            method: 'POST',
                                            body: formData
                                        });
            return response;
        } catch (error) {
            return error;
        }
    }

    form.addEventListener("submit", submit);
});