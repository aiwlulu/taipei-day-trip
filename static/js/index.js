document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.getElementById("search-bar");
  const inputField = document.getElementById("input-field");
  const attractionsContainer = document.querySelector(".attraction-group");
  const attractionsEnd = document.querySelector(".attraction-end");
  const mrtList = document.querySelector(".mrts-list");
  const buttonLeft = document.querySelector(".button-left");
  const buttonRight = document.querySelector(".button-right");

  let mrts = [];
  let nextPage = 0;
  let loading = false;

  const hostname = window.location.host;
  const apiBaseUrl = `http://${hostname}/api`;

  function fetchData(url) {
    return fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  }

  function clearAttractions() {
    attractionsContainer.innerHTML = "";
  }

  function loadAttractions() {
    if (loading || nextPage === null) return;

    loading = true;
    const keyword = inputField.value.trim();

    fetchData(
      `${apiBaseUrl}/attractions?page=${nextPage}&keyword=${keyword}`
    ).then((data) => {
      if (data.data.length === 0) {
        attractionsContainer.textContent = "沒有符合條件的結果";
        nextPage = null;
      } else {
        data.data.forEach((attraction) => {
          const attractionItem = document.createElement("div");
          attractionItem.classList.add("attraction-item");

          attractionItem.addEventListener("click", () => {
            const attractionId = attraction.id;

            window.location.href = `/attraction/${attractionId}`;
          });

          const mrtText = attraction.mrt ? attraction.mrt : "無鄰近捷運站";

          attractionItem.innerHTML = `
                        <img src="${attraction.images[0] || ""}" alt="">
                        <div class="attr-name">${attraction.name}</div>
                        <div class="attr-container">
                            <div class="attr-mrt">${mrtText}</div>
                            <div class="attr-category">${
                              attraction.category
                            }</div>
                        </div>
                    `;

          attractionsContainer.appendChild(attractionItem);
        });

        nextPage = data.nextPage;
      }

      loading = false;
    });
  }

  function renderMRTList() {
    mrtList.innerHTML = "";

    mrts.forEach((mrtName) => {
      const mrtItem = document.createElement("div");
      mrtItem.classList.add("mrt-item");
      mrtItem.textContent = mrtName;
      mrtList.appendChild(mrtItem);

      mrtItem.addEventListener("click", () => {
        inputField.value = mrtName;
        searchForm.dispatchEvent(new Event("submit"));
      });
    });
  }

  function submitForm(event) {
    event.preventDefault();
    clearAttractions();
    nextPage = 0;
    loadAttractions();
  }

  function scrollMrtList(direction) {
    const mrtItemWidth = mrtList
      .querySelector(".mrt-item")
      .getBoundingClientRect().width;
    const windowWidth = window.innerWidth;
    let scrollDistance;

    if (windowWidth > 1200) {
      scrollDistance = mrtItemWidth * 18;
    } else if (windowWidth > 600) {
      scrollDistance = mrtItemWidth * 8;
    } else {
      scrollDistance = mrtItemWidth * 3;
    }

    if (direction === "left") {
      mrtList.scrollBy({
        left: -scrollDistance,
        behavior: "smooth",
      });
    } else if (direction === "right") {
      mrtList.scrollBy({
        left: scrollDistance,
        behavior: "smooth",
      });
    }
  }

  // IntersectionObserver API
  const observerOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 1.0,
  };

  function observerCallback(entries, observer) {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !loading) {
        loadAttractions();
      }
    });
  }

  fetchData(`${apiBaseUrl}/mrts`).then((data) => {
    if (data && data.data) {
      mrts = data.data;
      renderMRTList();
    } else {
      console.error("Invalid data received from the server");
    }
  });

  const observer = new IntersectionObserver(observerCallback, observerOptions);

  observer.observe(attractionsEnd);

  searchForm.addEventListener("submit", submitForm);

  buttonLeft.addEventListener("click", () => {
    scrollMrtList("left");
  });

  buttonRight.addEventListener("click", () => {
    scrollMrtList("right");
  });

  loadAttractions();
});
