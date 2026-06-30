"use strict";

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".spoiler-toggle").forEach(function(button) {
        button.addEventListener("click", function() {
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
        });
    });
});