"use strict";
import { postVote } from "./api.js";

document.addEventListener("DOMContentLoaded", function() {
    const upvoteButtons = document.getElementsByClassName("upvote_button");
    const arrowImgs = document.getElementsByClassName("upvote_img");
    const unselectedImg = 'up_arrow_white.png'
    const selectedImg = 'up_arrow_green.png'
    const imgFolderPath = '/static/assets/images/';

    async function toggleUpvote(e) {
        const thingName = e.currentTarget.parentElement.id;
        const categoryName = e.currentTarget.parentElement.parentElement.parentElement.id;
        const arrowImg = e.currentTarget.firstElementChild;
        const src = arrowImg.getAttribute('src');

        if (src.endsWith(unselectedImg)) {
            const arrowImgsForCategory = Array.from(arrowImgs)
                .filter(e => e.parentElement.parentElement.parentElement.parentElement.id == categoryName);
            arrowImgsForCategory.forEach(e => e.setAttribute('src', imgFolderPath+unselectedImg));
            arrowImg.setAttribute('src', imgFolderPath+selectedImg);
        } else {
            arrowImg.setAttribute('src', imgFolderPath+unselectedImg);
        }

        const success = await postVote(categoryName, thingName);
        if (!success)
            alert("error on our end adding vote! sorry!")
    }

    Array.from(upvoteButtons).forEach(element => {
        element.addEventListener("click", toggleUpvote)
    });
});