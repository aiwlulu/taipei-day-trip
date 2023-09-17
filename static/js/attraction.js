// tourFee
const morningRadio = document.getElementById("morning");
const afternoonRadio = document.getElementById("afternoon");
const tourFeeElement = document.getElementById("tour-fee");

morningRadio.addEventListener("change", updateTourFee);
afternoonRadio.addEventListener("change", updateTourFee);

function updateTourFee() {
  const selectedTime = morningRadio.checked ? "morning" : "afternoon";
  let tourFee = 2000;

  if (selectedTime === "afternoon") {
    tourFee = 2500;
  }

  tourFeeElement.textContent = `新台幣 ${tourFee} 元`;
}

updateTourFee();

// currentDate
let currentDate = new Date();
let timezoneOffset = -8 * 60;

currentDate.setMinutes(currentDate.getMinutes() + timezoneOffset);

let currentFormatted = currentDate.toISOString().split("T")[0];

let dateInput = document.getElementById("date-input");

dateInput.setAttribute("min", currentFormatted);

// get Attraction info
document.addEventListener("DOMContentLoaded", async function () {
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
  imgContainer.src = attraction.images[0];

  const nameElement = document.querySelector(".profile .name");
  nameElement.textContent = attraction.name;

  const categoryElement = document.querySelector(".profile .category");
  categoryElement.textContent = attraction.category;

  const mrtElement = document.querySelector(".profile .mrt");
  mrtElement.textContent = attraction.mrt;

  const descriptionElement = document.querySelector("#description");
  descriptionElement.textContent = attraction.description;

  const addressElement = document.querySelector("#address");
  addressElement.textContent = attraction.address;

  const transportElement = document.querySelector("#transport");
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
