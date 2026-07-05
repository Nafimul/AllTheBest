document.addEventListener('DOMContentLoaded', () => {
    const searchBox = document.getElementById('global-search-input');
    const searchTypeInputs = document.querySelectorAll('input[name="search-type"]');
    const suggestionsBox = document.getElementById('global-search-suggestions');
    const searchForm = document.getElementById('global-search-form');

    if (!searchBox || !suggestionsBox || !searchForm) {
        return;
    }

    let activeIndex = -1;
    let currentSuggestions = [];

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
                    <button type="button" class="search-suggestion" data-index="${index}" data-name="${item.name}">
                        ${item.name}
                    </button>
                `,
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

    const lookupSuggestions = async (query) => {
        const type = document.querySelector('input[name="search-type"]:checked')?.value || 'thing';
        if (!query.trim()) {
            hideSuggestions();
            return;
        }

        const response = await fetch(`/api/search?type=${type}&q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            return;
        }

        const suggestions = await response.json();
        setSuggestions(suggestions);
    };

    searchBox.addEventListener('input', () => {
        const query = searchBox.value.trim();
        if (query.length < 1) {
            hideSuggestions();
            return;
        }
        lookupSuggestions(query);
    });

    searchTypeInputs.forEach((input) => {
        input.addEventListener('change', () => {
            if (searchBox.value.trim()) {
                lookupSuggestions(searchBox.value.trim());
            }
        });
    });

    searchBox.addEventListener('keydown', (event) => {
        if (!currentSuggestions.length) {
            return;
        }

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            activeIndex = (activeIndex + 1) % currentSuggestions.length;
            highlightSuggestion(activeIndex);
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            activeIndex = (activeIndex - 1 + currentSuggestions.length) % currentSuggestions.length;
            highlightSuggestion(activeIndex);
        } else if (event.key === 'Enter' && activeIndex >= 0) {
            event.preventDefault();
            const selected = currentSuggestions[activeIndex];
            if (selected) {
                searchBox.value = selected.name;
                hideSuggestions();
                searchForm.submit();
            }
        } else if (event.key === 'Escape') {
            hideSuggestions();
        }
    });

    const highlightSuggestion = (index) => {
        const buttons = suggestionsBox.querySelectorAll('.search-suggestion');
        buttons.forEach((button, buttonIndex) => {
            button.classList.toggle('active', buttonIndex === index);
        });
    };

    searchForm.addEventListener('submit', (event) => {
        const selectedType = document.querySelector('input[name="search-type"]:checked')?.value || 'thing';
        const query = searchBox.value.trim();
        if (!query) {
            return;
        }

        searchForm.action = selectedType === 'category' ? '/categories' : '/things';
    });

    suggestionsBox.addEventListener('click', (event) => {
        const button = event.target.closest('.search-suggestion');
        if (!button) {
            return;
        }

        searchBox.value = button.dataset.name || '';
        hideSuggestions();
        const selectedType = document.querySelector('input[name="search-type"]:checked')?.value || 'thing';
        searchForm.action = selectedType === 'category' ? '/categories' : '/things';
        searchForm.submit();
    });

    document.addEventListener('click', (event) => {
        if (!searchForm.contains(event.target)) {
            hideSuggestions();
        }
    });
});
