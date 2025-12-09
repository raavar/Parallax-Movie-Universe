document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('autocompleteResults');
    let currentQuery = '';
    let searchTimeout;

    if (!searchInput) return;

    searchInput.addEventListener('keyup', function() {
        clearTimeout(searchTimeout);
        
        const query = searchInput.value.trim();
        if (query.length < 1) { // Minim 1 caracter pentru căutare
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
            return;
        }

        // Folosim un debounce pentru a nu trimite cereri la fiecare tastă
        searchTimeout = setTimeout(() => {
            fetchSuggestions(query);
        }, 300); // Așteaptă 300ms după ultima tastă
    });

    async function fetchSuggestions(query) {
        const url = `/search_autocomplete?q=${encodeURIComponent(query)}`;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            displaySuggestions(data);
        } catch (error) {
            console.error('Eroare la preluarea sugestiilor:', error);
            resultsContainer.innerHTML = '<li>Eroare la încărcare.</li>';
            resultsContainer.style.display = 'block';
        }
    }

    function displaySuggestions(suggestions) {
        resultsContainer.innerHTML = '';
        
        if (suggestions.length === 0) {
            resultsContainer.style.display = 'none';
            return;
        }

        const ul = document.createElement('ul');
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = suggestion.url;
            a.textContent = suggestion.title;
            li.appendChild(a);
            ul.appendChild(li);
        });

        resultsContainer.appendChild(ul);
        resultsContainer.style.display = 'block';
    }

    // Ascunde rezultatele când focusul iese din câmpul de căutare
    searchInput.addEventListener('blur', () => {
        setTimeout(() => {
            resultsContainer.style.display = 'none';
        }, 150); // Mic delay pentru a permite click-ul pe link
    });

    // Afișează din nou rezultatele la focus
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.trim().length >= 2 && resultsContainer.innerHTML) {
             resultsContainer.style.display = 'block';
        }
    });
});