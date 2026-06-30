"use strict";

document.addEventListener("DOMContentLoaded", function() {
    // Handle spoiler toggle buttons
    document.querySelectorAll(".spoiler-toggle").forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            event.stopPropagation();
            handleSpoilerToggle(button);
        });
    });

    // Handle spoiler toggle images
    document.querySelectorAll(".spoiler-toggle-image").forEach(function(image) {
        image.addEventListener("click", function(event) {
            event.preventDefault();
            event.stopPropagation();
            const button = image.closest("li").querySelector(".spoiler-toggle");
            if (button) {
                handleSpoilerToggle(button);
            }
        });
    });
});

function handleSpoilerToggle(button) {
    const target = button.getAttribute("data-link-target") || "";
    const thingName = button.getAttribute("data-thing-name") || "";
    const spoilerFor = button.getAttribute("data-spoiler-for") || "";
    const isRevealed = button.dataset.revealed === "true";

    if (isRevealed) {
        window.location.href = target;
        return;
    }

    button.dataset.revealed = "true";
    button.textContent = thingName;
    button.classList.add("spoiler-revealed");

    const container = button.closest("li, tr, .profile-vote-card");
    if (container) {
        container.querySelectorAll(".spoiler-image").forEach(function(image) {
            image.classList.remove("spoiler-image");
            image.classList.add("spoiler-image-revealed");
        });
    }

    if (spoilerFor) {
        button.setAttribute("title", `Spoiler for ${spoilerFor}`);
    }
}