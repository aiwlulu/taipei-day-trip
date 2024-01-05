async function fetchOrderList() {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("Unauthorized: No token provided.");
    }

    const response = await fetch("/api/orders/history", {
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
      displayOrders(data.data);
    } else {
      document.getElementById("order-list").innerHTML = "<p>尚無訂單。</p>";
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("order-list").innerHTML =
      "<p>無法獲取訂單歷史，請稍後再試。</p>";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchOrderList();
});

function displayOrders(orders) {
  const orderListElement = document.getElementById("order-list");
  orderListElement.innerHTML = "";

  if (orders.length === 0) {
    orderListElement.innerHTML = "<p>尚無訂單。</p>";
  } else {
    orders.forEach((order) => {
      const formattedPrice = `TWD ${new Intl.NumberFormat("zh-TW", {
        maximumFractionDigits: 0,
      }).format(order.price)}`;
      const orderElement = document.createElement("div");
      orderElement.classList.add("order-item");
      orderElement.innerHTML = `
                <div class="order-number">訂單號碼: ${order.number}</div>
                <span class="order-price">${formattedPrice}</span>
                <img class="order-img" src="${
                  order.trip.attraction.image
                }" alt="${order.trip.attraction.name}">
                <div class="order-details">
                  <h3>${order.trip.attraction.name}</h3>
                  <div class="date-time">
                    <img src="static/img/calendar.png" alt="Date">
                    <p>${order.trip.date}</p>
                  </div>
                  <div class="date-time">
                    <img src="static/img/clock.png" alt="Time">
                    <p>${order.trip.time}</p>
                  </div>
                  <p>聯絡人姓名: ${order.contact.name}</p>
                  <p>聯絡人郵件: ${order.contact.email}</p>
                  <p>聯絡人手機: ${order.contact.phone}</p>
                  <p>付款狀態: ${order.status === 0 ? "已付款" : "未付款"}</p>
                </div>
              `;
      orderListElement.appendChild(orderElement);
    });
  }
}
