"use strict";

document.addEventListener("DOMContentLoaded", function() {
    const form = document.forms.namedItem("addForm");
    const formMessage = document.getElementById("formMessage");
    const successMessage = document.getElementById("successMessage");
    const thingImage = document.getElementById("thingImage");
    const imagePreview = document.getElementById("imagePreview");
    const categoryIsNegativeEl = document.getElementById("categoryIsNegative");
    const categoryNamePrefixEl = document.getElementById("categoryNamePrefix");

    function changeIsNegative(e) {
        if (e.target.value === "LEAST FAVORITE" || e.target.value === "LEAST")
            categoryIsNegativeEl.checked = true;
        else {
            categoryIsNegativeEl.checked = false;
        }
    }
    categoryNamePrefixEl.addEventListener("change", changeIsNegative);

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
        const formData = new FormData(form);

        const categoryNameWithoutPrefix = formData.get("categoryName").trim().toUpperCase();
        const categoryNamePrefix = formData.get("categoryNamePrefix").trim().toUpperCase();
        const thingName = formData.get("thingName").trim().toUpperCase();
        const categoryName = categoryNamePrefix + " " + categoryNameWithoutPrefix;
        formData.set("categoryName", categoryName);
        formData.set("categoryNamePrefix", categoryNamePrefix);
        formData.set("thingName", thingName);
        if (formData.get("fromThing"))
            formData.set("fromThing", formData.get("fromThing").trim().toUpperCase());

        formMessage.innerText = "";

        let isSuccess = true;
        let isAddingCategory = false;
        let isAddingThing = false;
        let isAddingVote = false;
        
        if (categoryNameWithoutPrefix !== "")
            isAddingCategory = true;
        if (thingName !== "")
            isAddingThing = true;
        if (isAddingCategory && isAddingThing)
            isAddingVote = true;
        if (!isAddingCategory && !isAddingThing) {
            formMessage.innerText = "Please fill in either a category name or a thing name.";
            return;
        }

        if (isAddingThing) {
            const result = await postFormToApi(formData, "/api/thing");
            if (!result)
                isSuccess = false;
        }
        if (isAddingCategory) {
            const result = await postFormToApi(formData, "/api/category");
            if (!result)
                isSuccess = false;
        }
        if (isAddingVote) {
            const result = await postFormToApi(formData, "/api/vote");
            if (!result)
                isSuccess = false;
        }
        
        if (isSuccess)
            if (isAddingVote)
                formMessage.innerText = "successfully added vote for " + thingName + " in " + categoryName;
            else {
                if (isAddingThing)
                    formMessage.innerText = "successfully added " + thingName;
                if (isAddingCategory)
                    formMessage.innerText = "successfully added " + categoryName;
            }
        else
            formMessage.innerText = "Error!";
        
    }

    async function postFormToApi(formData, url) {
        try {
            const response = await fetch(url,
                                        {
                                            method: 'POST',
                                            body: formData
                                        });
            if (!response.ok)
                return null;

            return await response.json();
        } catch (error) {
            return null;
        }
    }



    form.addEventListener("submit", submit);
});