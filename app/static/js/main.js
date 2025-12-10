document.addEventListener('DOMContentLoaded', function() {
    
    // =======================================================
    // 1. Logica Dropdown-ului de Profil
    // =======================================================
    const dropdownButton = document.getElementById('userDropdownButton');
    const dropdownMenu = document.getElementById('userDropdownMenu');

    if (dropdownButton) {
        dropdownButton.addEventListener('click', function(event) {
            // Previne propagarea click-ului pentru a nu declanșa imediat închiderea
            event.stopPropagation(); 
            // Comută clasa 'show' pentru a afișa/ascunde meniul
            dropdownMenu.classList.toggle('show');
        });
    }
    
    // Închide dropdown-ul dacă se dă click în afara lui (pe tot documentul)
    window.addEventListener('click', function(event) {
        // Verifică dacă există meniul și dacă este deschis
        if (dropdownMenu && dropdownMenu.classList.contains('show')) {
            // Verifică dacă click-ul NU a fost pe butonul trigger SAU în interiorul meniului
            if (!event.target.closest('.user-dropdown')) {
                dropdownMenu.classList.remove('show');
            }
        }
    });

    
    // =======================================================
    // 2. Logica Autocomplete (Căutare)
    // =======================================================
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('autocompleteResults');
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

        searchTimeout = setTimeout(() => {
            fetchSuggestions(query);
        }, 300); // Debounce
    });

    async function fetchSuggestions(query) {
        const url = `/search_autocomplete?q=${encodeURIComponent(query)}`;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                // Tratează codurile HTTP eșuate, de ex. 500
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

    // Prevents the input from losing focus when clicking inside the results
    // (Păstrează rezultatele afișate când utilizatorul dă click pe un film)
    resultsContainer.addEventListener('mousedown', function(e) {
        e.preventDefault(); 
    });

    // Ascunde rezultatele când focusul iese din câmpul de căutare
    searchInput.addEventListener('blur', () => {
        // Folosim un mic timeout pentru a permite evenimentului mousedown de pe rezultate să se declanșeze
        setTimeout(() => {
            resultsContainer.style.display = 'none';
        }, 150);
    });

    // Afișează din nou rezultatele la focus (dacă există conținut)
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.trim().length >= 1 && resultsContainer.innerHTML) {
             resultsContainer.style.display = 'block';
        }
    });
});