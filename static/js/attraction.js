document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById('search-bar');
    const inputField = document.getElementById('input-field');
    const attractionsContainer = document.querySelector('.attraction-group');
  
    let nextPage = 0;
    let loading = false;
  
    function clearAttractions() {
        attractionsContainer.innerHTML = '';
    }
  
    function loadAttractions() {
        if (loading || nextPage === null) return;
  
        loading = true;
        const keyword = inputField.value.trim();
  
        const hostname = window.location.host;
        const apiBaseUrl = `http://${hostname}/api`;
  
        fetch(`${apiBaseUrl}/attractions?page=${nextPage}&keyword=${keyword}`)
            .then(response => response.json())
            .then(data => {
                if (data.data.length === 0) {
                    attractionsContainer.textContent = '沒有符合條件的結果';
                    nextPage = null;
                } else {
                    data.data.forEach(attraction => {
                        const attractionItem = document.createElement('div');
                        attractionItem.classList.add('attraction-item');
  
                        const mrtText = attraction.mrt ? attraction.mrt : '無鄰近捷運站';
  
                        attractionItem.innerHTML = `
                            <img src="${attraction.images[0] || ''}" alt="">
                            <div class="attr-name">${attraction.name}</div>
                            <div class="attr-container">
                                <div class="attr-mrt">${mrtText}</div>
                                <div class="attr-category">${attraction.category}</div>
                            </div>
                        `;
  
                        attractionsContainer.appendChild(attractionItem);
                    });
  
                    nextPage = data.nextPage;
                }
  
                loading = false;
            })
            .catch(error => {
                console.error('發生錯誤：', error);
                loading = false;
            });
    }
  
    searchForm.addEventListener('submit', function (e) {
        e.preventDefault();
        clearAttractions();
        nextPage = 0;
        loadAttractions();
    });
  
    loadAttractions();
  
    window.addEventListener('scroll', function () {
        const scrollHeight = document.documentElement.scrollHeight;
        const scrollTop = window.scrollY;
        const clientHeight = document.documentElement.clientHeight;
  
        if (scrollTop + clientHeight >= scrollHeight - 100 && !loading) {
            loadAttractions();
        }
    });
  });
  