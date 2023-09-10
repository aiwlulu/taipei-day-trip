const mrtList = document.querySelector('.mrts-list');
const searchBar = document.querySelector('#input-field');
const buttonLeft = document.querySelector('.button-left');
const buttonRight = document.querySelector('.button-right');
const form = document.getElementById("search-bar");

let mrts = [];

const hostname = window.location.host;
const apiBaseUrl = `http://${hostname}/api`;

fetch(`${apiBaseUrl}/mrts`, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    },
})
.then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
})
.then(data => {
    if (data && data.data) {
        mrts = data.data;
        renderMRTList();
    } else {
        console.error('Invalid data received from the server');
    }
})
.catch(error => {
    console.error('There was a problem with the fetch operation:', error);
});

function renderMRTList() {
    mrtList.innerHTML = '';

    mrts.forEach(mrtName => {
        const mrtItem = document.createElement('div');
        mrtItem.classList.add('mrt-item');
        mrtItem.textContent = mrtName;
        mrtList.appendChild(mrtItem);

        mrtItem.addEventListener('click', () => {
            searchBar.value = mrtName;
            form.dispatchEvent(new Event('submit'));
        });
    });
}

function submitForm(event) {
    event.preventDefault();
}

form.addEventListener('submit', submitForm);


function scrollMrtList(direction) {
    const mrtItem = document.querySelector('.mrt-item');
    const mrtItemWidth = mrtItem.getBoundingClientRect().width;
    const windowWidth = window.innerWidth;
    let scrollDistance;
    
    if (windowWidth > 1200) {
        scrollDistance = mrtItemWidth * 18;
    } else if (windowWidth > 600) {
        scrollDistance = mrtItemWidth * 8;
    } else {
        scrollDistance = mrtItemWidth * 3;
    }

    if (direction === 'left') {
        mrtList.scrollBy({
            left: -scrollDistance,
            behavior: 'smooth'
        });
    } else if (direction === 'right') {
        mrtList.scrollBy({
            left: scrollDistance,
            behavior: 'smooth'
        });
    }
}

buttonLeft.addEventListener('click', () => {
    scrollMrtList('left');
});

buttonRight.addEventListener('click', () => {
    scrollMrtList('right');
});
