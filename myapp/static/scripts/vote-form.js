"use strict";
import { sendFormToApi } from "./api.js";
import { addFromThingInput, removeEmptyFromThingNames, submitVoteForm } from "./form-helpers.js";

document.addEventListener("DOMContentLoaded", function() {
    const form = document.forms.namedItem("addForm");
    if (!form) {
        return;
    }

    const thingImage = document.getElementById("thingImage");
    const imagePreview = document.getElementsByClassName("imagePreview")[0];
    const categoryIsNegativeEl = document.getElementById("categoryIsNegative");
    const categoryNamePrefixEl = document.getElementById("categoryNamePrefix");
    const categoryNameEl = document.getElementById("categoryName");
    const fromThingInput = document.getElementsByClassName("fromThingNames")[0];
    const addFromThingButton = document.getElementById("fromThingButton");
    const formMessage = document.getElementById("formMessage");


    categoryNamePrefixEl.addEventListener("change", changeIsNegative);
    thingImage.addEventListener("change", previewImage);
    form.addEventListener("submit", e => formMessage.innerText = submitVoteForm(e));
    categoryNameEl.addEventListener("change", removeExtraPrefix);
    console.log(document.getElementById("fromThings"));
    addFromThingButton.addEventListener("click", e => addFromThingInput(document.getElementById("fromThings").querySelector(".search-input-wrapper")));

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
});