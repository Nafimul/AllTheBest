"use strict";

import { getThingJson, getCategoryJson } from "./api.js";

document.addEventListener('DOMContentLoaded', () => {
    const searchEls = document.querySelectorAll('.search-bar');
    const globalsearchForm = document.getElementById("globalSearchForm");

    async function autofillThingForm(thingName) {
        const imagePreview = thingForm.getElementById("imagePreview");
        const thingJson = await getThingJson(thingName);
        if (!thingJson)
            return;
        imagePreview.src = thingJson["img_path"];
    }

    async function autofillCategoryForm(categoryName) {
        const addForm = document.getElementById("addForm");
        const categoryJson = await getCategoryJson(categoryName);
        if (!categoryJson)
            return;
        addForm.querySelector('input[name="categoryIsSpoiler"]').checked = categoryJson["is_spoiler"];
        addForm.querySelector('input[name="categoryIsNegative"]').checked = categoryJson["is_negative"];
        addForm.querySelector('input[name="categoryDesc"]').value = categoryJson["desc"];
    }

    searchEls.forEach((searchEl) => {
        const searchInput = searchEl.querySelector('input[type="text"]');
        const suggestionsBox = searchEl.querySelector('.search-suggestions');
        const searchTypeInputs = searchEl.querySelectorAll('input[name="search-type"]');

        if (!searchInput || !suggestionsBox) return;

        let activeIndex = -1;
        let currentSuggestions = [];

        const autofillForms = (searchTerm) => {
                console.log("out");
            if (searchInput.classList.contains("vote-input")) {
                console.log("oidfnanfio");
                if (searchInput.classList.contains("thing")) {
                    autofillThingForm(searchTerm);
                } else if (searchInput.classList.contains("category")) {
                    autofillCategoryForm(searchTerm);
                }
            }
        }

        const getSearchType = () => {
            // 1. try radio buttons inside this searchEl
            const selectedRadio = searchEl.querySelector('input[name="search-type"]:checked');
            if (selectedRadio) return selectedRadio.value;

            // 2. fallback to input class
            if (searchInput.classList.contains('category')) return 'category';
            if (searchInput.classList.contains('thing')) return 'thing';

            // 3. default
            return 'thing';
        };

        const setSuggestions = (items) => {
            currentSuggestions = items;
            activeIndex = -1;

            if (!items.length) {
                suggestionsBox.innerHTML = '';
                suggestionsBox.style.display = 'none';
                return;
            }

            suggestionsBox.innerHTML = items
                .map(
                    (item, index) => `
                        <button type="button"
                            class="search-suggestion"
                            data-index="${index}"
                            data-name="${item.name}">
                            ${item.name}
                        </button>
                    `
                )
                .join('');

            suggestionsBox.style.display = 'block';
        };

        const hideSuggestions = () => {
            suggestionsBox.innerHTML = '';
            suggestionsBox.style.display = 'none';
            currentSuggestions = [];
            activeIndex = -1;
        };

        const highlightSuggestion = (index) => {
            const buttons = suggestionsBox.querySelectorAll('.search-suggestion');
            buttons.forEach((btn, i) => {
                btn.classList.toggle('active', i === index);
            });
        };

        const lookupSuggestions = async (query) => {
            const type = getSearchType();

            if (!query.trim()) {
                hideSuggestions();
                return;
            }

            const response = await fetch(
                `/api/search?type=${type}&q=${encodeURIComponent(query)}`
            );

            if (!response.ok) return;

            const suggestions = await response.json();
            setSuggestions(suggestions);
        };

        // INPUT
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();

            if (query.length < 1) {
                hideSuggestions();
                return;
            }

            lookupSuggestions(query);
        });

        // RADIO CHANGE (only if exists)
        searchTypeInputs.forEach((input) => {
            input.addEventListener('change', () => {
                const query = searchInput.value.trim();
                if (query) lookupSuggestions(query);
            });
        });

        // KEYBOARD NAV
        searchInput.addEventListener('keydown', (event) => {
            if (!currentSuggestions.length) return;

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                activeIndex = (activeIndex + 1) % currentSuggestions.length;
                highlightSuggestion(activeIndex);
            }

            if (event.key === 'ArrowUp') {
                event.preventDefault();
                activeIndex =
                    (activeIndex - 1 + currentSuggestions.length) %
                    currentSuggestions.length;
                highlightSuggestion(activeIndex);
            }

            if (event.key === 'Enter' && activeIndex >= 0) {
                event.preventDefault();
                const selected = currentSuggestions[activeIndex];
                if (selected) {
                    searchInput.value = selected.name;
                    autofillForms(selected.name);
                    hideSuggestions();
                }
            }

            if (event.key === 'Escape') {
                hideSuggestions();
            }
        });

        // CLICK SUGGESTION
        suggestionsBox.addEventListener('click', (event) => {
            const button = event.target.closest('.search-suggestion');
            if (!button) return;

            searchInput.value = button.dataset.name || '';
            autofillForms(button.dataset.name || '');
            hideSuggestions();
        });

        // SUBMIT
        globalsearchForm.addEventListener('submit', (event) => {
            const query = searchInput.value.trim();
            if (!query) return;

            searchEl.action = getSearchType() === 'category'
                ? '/categories'
                : '/things';
        }, { once: true });

        // OUTSIDE CLICK (scoped per searchEl)
        document.addEventListener('click', (event) => {
            if (!searchEl.contains(event.target)) {
                hideSuggestions();
            }
        });
    });
});