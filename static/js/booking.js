const bookingSection = document.querySelector(".booking-container");
const attractionImage = document.getElementById("attraction-image");
const attractionName = document.getElementById("attraction-name");
const attractionAddress = document.getElementById("address");
const date = document.getElementById("date");
const time = document.getElementById("time");
const price = document.getElementById("price");
const totalPrice = document.getElementById("total-price");
const username = document.getElementById("username");
const contactName = document.getElementById("contactName");
const contactEmail = document.getElementById("contactEmail");
const cardNumber = document.getElementById("cardNumber");
const expirationDate = document.getElementById("expirationDate");
const cvv = document.getElementById("cvv");
const deleteIcon = document.querySelector(".icon-delete");

// UserInfo
async function getUserInfo() {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      return;
    }

    const response = await fetch("/api/user/auth", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error：${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (data.data) {
      username.textContent = data.data.name;
      contactName.value = data.data.name;
      contactEmail.value = data.data.email;
    }
  } catch (error) {
    console.error("發生錯誤：", error);
  }
}

// BookingInfo
async function getBookings() {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      return;
    }

    const response = await fetch("/api/booking", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error：${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (data.data && data.data.length > 0) {
      const bookingData = data.data[0];

      attractionImage.src = bookingData.attraction_image;
      attractionName.textContent = bookingData.attraction_name;
      attractionAddress.textContent = bookingData.attraction_address;

      let bookingDate = new Date(bookingData.date);
      date.textContent = bookingDate.toISOString().split("T")[0];

      time.textContent =
        bookingData.time === "09:00"
          ? "早上 9 點到下午 1 點"
          : "下午 1 點到下午 6 點";

      price.textContent = `新台幣 ${bookingData.price} 元`;
      totalPrice.textContent = `總價：新台幣 ${bookingData.price} 元`;

      bookingSection.style.display = "block";
    } else {
      const noBookingMessage = document.querySelector(".no-booking");
      bookingSection.style.display = "none";
      noBookingMessage.style.display = "block";
    }
  } catch (error) {
    console.error("發生錯誤：", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  getBookings();
  getUserInfo();
});

// DeleteBooking
async function deleteBooking() {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      return;
    }

    const response = await fetch("/api/booking", {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error：${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (data.ok) {
      window.location.reload();
    }
  } catch (error) {
    console.error("發生錯誤：", error);
  }
}

deleteIcon.addEventListener("click", deleteBooking);

// cardFormat
cardNumber.addEventListener("input", function () {
  this.value = this.value
    .replace(/\D/g, "")
    .replace(/(\d{4})/g, "$1 ")
    .trim();
});

expirationDate.addEventListener("input", function () {
  this.value = this.value
    .replace(/\D/g, "")
    .replace(/(\d{2})/, "$1 / ")
    .trim();
});

cvv.addEventListener("input", function () {
  this.value = this.value.replace(/\D/g, "").substr(0, 3);
});
