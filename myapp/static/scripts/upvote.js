"use strict";
import { postVote } from "./api.js";

document.addEventListener("DOMContentLoaded", function() {
    const upvoteButtons = Array.from(document.getElementsByClassName("upvote_button"));
    const unselectedImg = 'up_arrow_white.png';
    const selectedImg = 'up_arrow_green.png';
    const imgFolderPath = '/static/assets/images/';

    function setCategoryArrows(categoryName, selectedButton) {
        upvoteButtons
            .filter(btn => btn.dataset.category === categoryName)
            .forEach(btn => {
                const img = btn.querySelector('.upvote_img');
                if (img) {
                    img.setAttribute('src', imgFolderPath + unselectedImg);
                }
            });

        const selectedImgEl = selectedButton.querySelector('.upvote_img');
        if (selectedImgEl) {
            selectedImgEl.setAttribute('src', imgFolderPath + selectedImg);
        }
    }

    async function toggleUpvote(e) {
        const button = e.currentTarget;
        const thingName = button.dataset.thing;
        const categoryName = button.dataset.category;
        const arrowImg = button.querySelector('.upvote_img');
        if (!thingName || !categoryName || !arrowImg) {
            return;
        }

        const src = arrowImg.getAttribute('src');
        if (src.endsWith(unselectedImg)) {
            setCategoryArrows(categoryName, button);
        } else {
            arrowImg.setAttribute('src', imgFolderPath + unselectedImg);
        }

        const success = await postVote(categoryName, thingName);
        if (!success) {
            alert("error on our end adding vote! Maybe you're not logged in?");
        }
    }

    upvoteButtons.forEach(element => {
        element.addEventListener("click", toggleUpvote);
    });
});