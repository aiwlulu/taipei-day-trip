const bookingSection = document.querySelector(".booking-container");
let attractionId;
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
    const userInfo = JSON.parse(localStorage.getItem("userInfo"));
    if (!userInfo) {
      return;
    }

    username.textContent = userInfo.name;
    contactName.value = userInfo.name;
    contactEmail.value = userInfo.email;
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
      attractionId = bookingData.attraction_id;
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
  if (window.checkUserLoginStatus && !window.userLoginStatusChecked) {
    window.checkUserLoginStatus();
    window.userLoginStatusChecked = true;
  }
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

// TapPay
TPDirect.setupSDK(
  137172,
  "app_RuNBDTN1soYHtkkY3kurGvYm77OPjTxWcNLgLm7wHfgxvCZ6gQy2McdyL18a",
  "sandbox"
);

TPDirect.card.setup({
  fields: {
    number: {
      element: "#card-number",
      placeholder: "**** **** **** ****",
    },
    expirationDate: {
      element: document.getElementById("card-expiration-date"),
      placeholder: "MM / YY",
    },
    ccv: {
      element: "#card-ccv",
      placeholder: "CVV",
    },
  },
  styles: {
    input: {
      color: "gray",
    },
    ".valid": {
      color: "green",
    },
    ".invalid": {
      color: "red",
    },
  },
  isMaskCreditCardNumber: true,
  maskCreditCardNumberRange: {
    beginIndex: 6,
    endIndex: 11,
  },
});

// Submit
const submitButton = document.getElementById("payment-button");

submitButton.addEventListener("click", async (event) => {
  event.preventDefault();
  if (submitButton.disabled) return;

  const contactNameValue = contactName.value.trim();
  const contactEmailValue = contactEmail.value.trim();
  const contactPhoneValue = contactPhone.value.trim();

  if (!contactNameValue || !contactEmailValue || !contactPhoneValue) {
    return alert("請填寫所有聯絡資訊");
  }

  if (
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactEmailValue) ||
    !/^[0-9]{10}$/.test(contactPhoneValue)
  ) {
    return alert("請輸入有效的聯絡信箱和手機號碼");
  }

  submitButton.disabled = true;

  try {
    const primeResult = await getTappayPrime();
    if (primeResult.status !== 0)
      throw new Error("獲取 prime 時出錯：" + primeResult.msg);

    const orderData = {
      prime: primeResult.card.prime,
      order: {
        attractionId: attractionId,
        date: date.textContent,
        time: time.textContent,
        price: parseFloat(price.textContent.replace(/新台幣|元|\s/g, "")),
        contact: {
          name: contactNameValue,
          email: contactEmailValue,
          phone: contactPhoneValue,
        },
      },
    };

    const createOrderResult = await createOrder(orderData);
    if (createOrderResult.message !== "Order created successfully") {
      throw new Error("訂單建立失敗：" + createOrderResult.message);
    }

    window.location.href = `/thankyou?number=${createOrderResult.order_number}`;
  } catch (error) {
    console.error("發生錯誤：", error);
    alert(error.message);
  } finally {
    submitButton.disabled = false;
  }
});

async function getTappayPrime() {
  return new Promise((resolve) => TPDirect.card.getPrime(resolve));
}

async function createOrder(orderData) {
  const token = localStorage.getItem("token");
  if (!token) throw new Error("未登入系統，拒絕存取");

  const response = await fetch("/api/orders", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(orderData),
  });

  if (!response.ok) {
    const errorMessage = await response.json();
    throw new Error(errorMessage.message);
  }

  return response.json();
}

TPDirect.card.onUpdate((update) => {
  submitButton.disabled = !update.canGetPrime;
});
