import { sendFormToApi } from "./api.js";


export function addFromThingInput(searchInputWrapper) {
    const clone = searchInputWrapper.cloneNode(true);
    clone.value = "";
    clone.id = null;
    searchInputWrapper.parentElement.appendChild(clone);
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

export async function submitVoteForm(e) {
    e.preventDefault();
    const formMessage = e.currentTarget.querySelector(".formMessage");
    const formData = new FormData(e.currentTarget);

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
    
    if (categoryNameWithoutPrefix)
        isAddingCategory = true;
    if (thingName)
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