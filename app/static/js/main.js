document.addEventListener('DOMContentLoaded', function() {
    console.log("Main.js loaded!");

    // 1. DROPDOWN
    const dropdownButton = document.getElementById('userDropdownButton');
    const dropdownMenu = document.getElementById('userDropdownMenu');

    if (dropdownButton) {
        dropdownButton.addEventListener('click', function(event) {
            event.stopPropagation(); 
            dropdownMenu.classList.toggle('show');
        });
    }
    
    window.addEventListener('click', function(event) {
        if (dropdownMenu && dropdownMenu.classList.contains('show')) {
            if (!event.target.closest('.user-dropdown')) {
                dropdownMenu.classList.remove('show');
            }
        }
    });

    // 2. AUTOCOMPLETE (Corectat)
    // CORECȚIE: Folosim ID-ul 'searchBox' care există în HTML
    const searchInput = document.getElementById('searchBox'); 
    const resultsContainer = document.getElementById('autocompleteResults');
    let searchTimeout;

    if (searchInput && resultsContainer) {
        console.log("Search elements found.");

        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            clearTimeout(searchTimeout);

            if (query.length < 1) { 
                resultsContainer.style.display = 'none';
                return;
            }

            // Debounce 300ms
            searchTimeout = setTimeout(() => {
                console.log("Searching for:", query);
                fetch(`/search_autocomplete?q=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) throw new Error("Network error");
                        return response.json();
                    })
                    .then(data => {
                        console.log("Results:", data);
                        resultsContainer.innerHTML = '';
                        
                        if (data.length > 0) {
                            const ul = document.createElement('ul');
                            ul.style.listStyle = 'none';
                            ul.style.margin = '0';
                            ul.style.padding = '0';

                            data.forEach(movie => {
                                const li = document.createElement('li');
                                const a = document.createElement('a');
                                a.href = movie.url;
                                a.textContent = movie.title;
                                // Stiluri directe pentru siguranță
                                a.style.display = 'block';
                                a.style.padding = '10px 15px';
                                a.style.color = '#ccc';
                                a.style.textDecoration = 'none';
                                a.style.borderBottom = '1px solid #444';
                                
                                a.onmouseover = () => { a.style.backgroundColor = '#333'; a.style.color = '#fff'; };
                                a.onmouseout = () => { a.style.backgroundColor = 'transparent'; a.style.color = '#ccc'; };

                                li.appendChild(a);
                                ul.appendChild(li);
                            });
                            resultsContainer.appendChild(ul);
                            resultsContainer.style.display = 'block';
                        } else {
                            resultsContainer.style.display = 'none';
                        }
                    })
                    .catch(err => console.error("Search error:", err));
            }, 300);
        });

        // Ascunde la click în afară
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.style.display = 'none';
            }
        });
    } else {
        console.error("ERROR: searchBox element not found in HTML");
    }
});