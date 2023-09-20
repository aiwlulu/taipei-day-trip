// tourFee
const morningRadio = document.getElementById("morning");
const afternoonRadio = document.getElementById("afternoon");
const tourFeeElement = document.getElementById("tour-fee");

function updateTourFee() {
  const tourFee = morningRadio.checked ? 2000 : 2500;
  tourFeeElement.textContent = `新台幣 ${tourFee} 元`;
}

morningRadio.addEventListener("change", updateTourFee);
afternoonRadio.addEventListener("change", updateTourFee);
updateTourFee();

// currentDate
const dateInput = document.getElementById("date-input");
const timezoneOffset = -8 * 60;
const currentDate = new Date();
currentDate.setMinutes(currentDate.getMinutes() + timezoneOffset);
const currentFormatted = currentDate.toISOString().split("T")[0];
dateInput.setAttribute("min", currentFormatted);

// Attraction info
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const hostname = window.location.host;
    const apiBaseUrl = `http://${hostname}/api`;
    const attractionId = getAttractionIdFromURL();
    const response = await fetch(`${apiBaseUrl}/attraction/${attractionId}`);

    if (!response.ok) {
      throw new Error(`Error：${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (data.data) {
      displayAttractionInfo(data.data);
      initializeCarousel(data.data.images);
    } else {
      console.error(data.message);
    }
  } catch (error) {
    console.error("Error：", error);
  }
});

function getAttractionIdFromURL() {
  const pathSegments = window.location.pathname.split("/");
  return pathSegments[pathSegments.length - 1];
}

function displayAttractionInfo(attraction) {
  const imgContainer = document.querySelector(".img-container img");
  const nameElement = document.querySelector(".profile .name");
  const categoryElement = document.querySelector(".profile .category");
  const mrtElement = document.querySelector(".profile .mrt");
  const descriptionElement = document.querySelector("#description");
  const addressElement = document.querySelector("#address");
  const transportElement = document.querySelector("#transport");

  imgContainer.src = attraction.images[0];
  nameElement.textContent = attraction.name;
  categoryElement.textContent = attraction.category;
  mrtElement.textContent = attraction.mrt;
  descriptionElement.textContent = attraction.description;
  addressElement.textContent = attraction.address;
  transportElement.textContent = attraction.transport;
}

// Carousel function
async function initializeCarousel(images) {
  const imgContainer = document.querySelector(".img-container img");
  const buttonLeft = document.querySelector(".button-left");
  const buttonRight = document.querySelector(".button-right");
  const dotContainer = document.getElementById("dot-container");

  let currentImageIndex = 0;

  function updateImage() {
    imgContainer.src = "";
    const img = new Image();
    img.onload = () => {
      imgContainer.src = img.src;
    };
    img.src = images[currentImageIndex];
  }

  function updateActiveDot() {
    const dots = document.querySelectorAll(".dot");
    dots.forEach((dot, index) => {
      if (index === currentImageIndex) {
        dot.classList.add("dot--active");
      } else {
        dot.classList.remove("dot--active");
      }
    });
  }

  function prevImage() {
    currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
    updateImage();
    updateActiveDot();
  }

  function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % images.length;
    updateImage();
    updateActiveDot();
  }

  buttonLeft.addEventListener("click", prevImage);
  buttonRight.addEventListener("click", nextImage);

  // Create dots
  for (let i = 0; i < images.length; i++) {
    const dot = document.createElement("span");
    dot.classList.add("dot");
    if (i === 0) {
      dot.classList.add("dot--active");
    }
    dot.addEventListener("click", () => {
      currentImageIndex = i;
      updateImage();
      updateActiveDot();
    });
    dotContainer.appendChild(dot);
  }

  for (let i = 0; i < images.length; i++) {
    const img = new Image();
    img.onload = () => {
      if (i === images.length - 1) {
        updateImage();
        updateActiveDot();
      }
    };
    img.src = images[i];
  }
}
