"use strict";
import { sendFormToApi } from "./api.js";

export function addFromThingInput(inputEl) {
    const clone = inputEl.cloneNode(false);
    clone.value = "";
    clone.id = null;
    inputEl.parentElement.appendChild(clone);
    return clone;
}

export function removeEmptyFromThingNames(formData, fieldName = "fromThingNames") {
    let fromThingNames = formData.getAll(fieldName);
    fromThingNames = fromThingNames.filter((name) => String(name).trim() !== "");
    formData.delete(fieldName);
    fromThingNames.forEach((name) => {
        formData.append(fieldName, name);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const form = document.forms.namedItem("addForm");
    if (!form) {
        return;
    }

    const formMessage = document.getElementById("formMessage");
    const thingImage = document.getElementById("thingImage");
    const imagePreview = document.getElementById("imagePreview");
    const categoryIsNegativeEl = document.getElementById("categoryIsNegative");
    const categoryNamePrefixEl = document.getElementById("categoryNamePrefix");
    const categoryNameEl = document.getElementById("categoryName");
    const fromThingInput = document.getElementById("fromThingNames");
    const addFromThingButton = document.getElementById("fromThingButton");

    categoryNamePrefixEl.addEventListener("change", changeIsNegative);
    thingImage.addEventListener("change", previewImage);
    form.addEventListener("submit", submit);
    categoryNameEl.addEventListener("change", removeExtraPrefix);
    addFromThingButton.addEventListener("click", addFromThingInput)

    function removeExtraPrefix(e) {
        let categoryName = e.currentTarget.value;
        const BUILTINPREFIXES = ["LEAST FAVORITE ", "FAVORITE ", "LEAST ", "MOST "];
        BUILTINPREFIXES.forEach( prefix => {
            if (categoryName.includes(prefix)) {
                categoryNamePrefixEl.value = prefix;
                e.currentTarget.value = categoryName.replace(prefix, "");
            };
        });
    }

    function changeIsNegative(e) {
        if (e.target.value === "LEAST FAVORITE" || e.target.value === "LEAST")
            categoryIsNegativeEl.checked = true;
        else {
            categoryIsNegativeEl.checked = false;
        }
    }

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

    async function submit(e) {
        e.preventDefault();
        const formData = new FormData(form);
        console.log(document.getElementById("categoryDesc").value);

        const categoryNameWithoutPrefix = formData.get("categoryName");
        const categoryNamePrefix = formData.get("categoryNamePrefix");
        const thingName = formData.get("thingName");
        const categoryName = categoryNamePrefix + " " + categoryNameWithoutPrefix;
        formData.set("categoryName", categoryName);
        formData.set("categoryNamePrefix", categoryNamePrefix);
        formData.set("thingName", thingName);
        removeEmptyFromThingNames(formData);

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
            const result = await sendFormToApi(formData, "/api/thing", "POST");
            if (!result)
                isSuccess = false;
        }
        if (isAddingCategory) {
            const result = await sendFormToApi(formData, "/api/category", "POST");
            if (!result)
                isSuccess = false;
        }
        if (isAddingVote) {
            const result = await sendFormToApi(formData, "/api/vote", "POST");
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

});