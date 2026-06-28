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
        const voteCountElement = button.closest('li')?.querySelector('.vote-count') || button.closest('tr')?.querySelector('.vote-count');
        if (!thingName || !categoryName || !arrowImg) {
            return;
        }

        const sameCategoryButtons = upvoteButtons.filter(btn => btn.dataset.category === categoryName);
        const previousSelectedButton = sameCategoryButtons.find(btn => {
            const img = btn.querySelector('.upvote_img');
            return img && img.getAttribute('src').endsWith(selectedImg);
        });
        const src = arrowImg.getAttribute('src');
        const isSelecting = src.endsWith(unselectedImg);

        if (isSelecting) {
            setCategoryArrows(categoryName, button);
        } else {
            arrowImg.setAttribute('src', imgFolderPath + unselectedImg);
        }

        const success = await postVote(categoryName, thingName);
        if (!success) {
            alert("error on our end adding vote! Maybe you're not logged in?");
            if (isSelecting) {
                arrowImg.setAttribute('src', imgFolderPath + unselectedImg);
            } else {
                arrowImg.setAttribute('src', imgFolderPath + selectedImg);
            }
            return;
        }

        if (voteCountElement) {
            const currentVotes = Number(voteCountElement.innerText.trim()) || 0;
            voteCountElement.innerText = isSelecting ? currentVotes + 1 : Math.max(currentVotes - 1, 0);
        }

        if (isSelecting && previousSelectedButton && previousSelectedButton !== button) {
            const previousVoteCount = previousSelectedButton.closest('li')?.querySelector('.vote-count') || previousSelectedButton.closest('tr')?.querySelector('.vote-count');
            if (previousVoteCount) {
                const previousVotes = Number(previousVoteCount.innerText.trim()) || 0;
                previousVoteCount.innerText = Math.max(previousVotes - 1, 0);
            }
        }
    }

    upvoteButtons.forEach(element => {
        element.addEventListener("click", toggleUpvote);
    });
});