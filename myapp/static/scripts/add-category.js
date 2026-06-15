"use strict";

document.addEventListener("DOMContentLoaded", function() {
    const form = document.forms.namedItem("categoryForm");
    console.log(form);
    const successMessage = document.getElementById("successMessage");

    async function submit(e) {
        e.preventDefault();
        let response = await postFormToApi(new FormData(form), "/api/category");
        if (response.ok) {
            let responseJson = await response.json()
            successMessage.innerText = responseJson["message"]
        }
        else
            successMessage.innerText = "Error adding category";
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