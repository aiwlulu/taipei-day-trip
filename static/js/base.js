const selectors = {
  loginRegister: ".login-register",
  dialogSignin: ".dialog-signin",
  dialogSignup: ".dialog-signup",
  registerLink: ".register-link",
  loginLink: ".login-link",
  closeSigninIcon: ".dialog-signin .icon-close",
  closeSignupIcon: ".dialog-signup .icon-close",
  dialogMask: ".dialog-mask",
  registerButton: ".register-button",
  registerName: "#register-name",
  registerEmail: "#register-email",
  registerPassword: "#register-password",
  registerMessage: ".register-message",
  loginButton: ".login-button",
  loginEmail: "#login-email",
  loginPassword: "#login-password",
  loginMessage: ".login-message",
};

const elements = {};

for (let key in selectors) {
  elements[key] = document.querySelector(selectors[key]);
}

// Loader
window.addEventListener("load", function () {
  let loaderWrapper = document.querySelector(".loader-wrapper");

  setTimeout(function () {
    loaderWrapper.style.display = "none";
  }, 200);
});

// Check login status & Logout
async function checkUserLoginStatus() {
  const token = localStorage.getItem("token");
  const logOut = document.querySelector(".logout");
  const loginRegister = document.querySelector(".login-register");

  if (token) {
    try {
      const response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Token invalid or expired");
      }

      const data = await response.json();

      if (data.data) {
        logOut.style.display = "block";
        loginRegister.style.display = "none";
      } else {
        throw new Error("No user data returned");
      }
    } catch (error) {
      console.error("Token validation error:", error);
      localStorage.removeItem("token");
      loginRegister.style.display = "block";
    }
  } else {
    loginRegister.style.display = "block";
  }
}

const logOut = document.querySelector(".logout");
logOut.addEventListener("click", function () {
  localStorage.removeItem("token");
  window.location.reload();
});

checkUserLoginStatus();

function toggleDialog(dialog, isActive, maskDisplay) {
  dialog.classList.toggle("active", isActive);
  elements.dialogMask.style.display = maskDisplay;
}

elements.loginRegister.addEventListener("click", function () {
  const token = localStorage.getItem("token");
  if (!token) {
    toggleDialog(elements.dialogSignin, true, "block");
  }
});

elements.closeSigninIcon.addEventListener("click", function () {
  toggleDialog(elements.dialogSignin, false, "none");
  elements.registerMessage.textContent = "";
  elements.loginMessage.textContent = "";
  elements.loginEmail.value = "";
  elements.loginPassword.value = "";
  elements.registerName.value = "";
  elements.registerEmail.value = "";
  elements.registerPassword.value = "";
});

elements.closeSignupIcon.addEventListener("click", function () {
  toggleDialog(elements.dialogSignup, false, "none");
  elements.registerMessage.textContent = "";
  elements.loginMessage.textContent = "";
  elements.loginEmail.value = "";
  elements.loginPassword.value = "";
  elements.registerName.value = "";
  elements.registerEmail.value = "";
  elements.registerPassword.value = "";
});

elements.registerLink.addEventListener("click", function () {
  toggleDialog(elements.dialogSignin, false);
  toggleDialog(elements.dialogSignup, true, "block");
  elements.registerMessage.textContent = "";
  elements.loginMessage.textContent = "";
});

elements.loginLink.addEventListener("click", function () {
  toggleDialog(elements.dialogSignup, false);
  toggleDialog(elements.dialogSignin, true, "block");
  elements.registerMessage.textContent = "";
  elements.loginMessage.textContent = "";
});

// Register
elements.registerButton.addEventListener("click", async function (event) {
  event.preventDefault();

  let name = elements.registerName.value;
  const email = elements.registerEmail.value;
  const password = elements.registerPassword.value;
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const passwordPattern = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}/;

  name = name.trim();
  if (name.length < 2) {
    alert("姓名至少需要 2 個字元");
    return;
  }

  if (!emailPattern.test(email)) {
    alert("請輸入有效的電子信箱");
    return;
  }

  if (!passwordPattern.test(password)) {
    alert(
      "密碼至少包含一個數字，一個小寫字母，一個大寫字母，一個特殊字符，並且至少有 8 個字元"
    );
    return;
  }

  const response = await fetch("/api/user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await response.json();

  if (response.ok) {
    elements.registerMessage.classList.remove("error");
    elements.registerMessage.textContent = "註冊成功！";
  } else {
    elements.registerMessage.classList.add("error");
    elements.registerMessage.textContent = data.message;
  }
});

// Login
elements.loginButton.addEventListener("click", async function (event) {
  event.preventDefault();

  const email = elements.loginEmail.value;
  const password = elements.loginPassword.value;

  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const passwordPattern = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}/;

  if (!emailPattern.test(email)) {
    alert("請輸入有效的電子信箱");
    return;
  }

  if (!passwordPattern.test(password)) {
    alert(
      "密碼至少包含一個數字，一個小寫字母，一個大寫字母，一個特殊字符，並且至少有 8 個字元"
    );
    return;
  }

  const response = await fetch("/api/user/auth", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (response.ok) {
    elements.loginMessage.classList.remove("error");
    elements.loginMessage.textContent = "登入成功！";

    localStorage.setItem("token", data.token);

    window.location.reload();
  } else {
    elements.loginMessage.classList.add("error");
    elements.loginMessage.textContent = data.message;
  }
});

// bookingLink
const bookingLink = document.querySelector(".booking");

bookingLink.addEventListener("click", async function () {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      toggleDialog(elements.dialogSignin, true, "block");
    } else {
      const response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (data.data) {
        window.location.href = "/booking";
      } else {
        toggleDialog(elements.dialogSignin, true, "block");
      }
    }
  } catch (error) {
    console.error("發生錯誤：", error);
  }
});

const path = window.location.pathname;
const token = localStorage.getItem("token");
if (!token && path.includes("/booking")) {
  window.location.href = "/";
}
