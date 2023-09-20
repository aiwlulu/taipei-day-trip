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
  loginRegisterButton: ".menu-item.login-register",
};

const elements = {};

for (let key in selectors) {
  elements[key] = document.querySelector(selectors[key]);
}

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

  const name = elements.registerName.value;
  const email = elements.registerEmail.value;
  const password = elements.registerPassword.value;

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

// Check login status & Logout
async function checkUserLoginStatus() {
  const token = localStorage.getItem("token");

  if (token) {
    const response = await fetch("/api/user/auth", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (data.data) {
      elements.loginRegisterButton.classList.add("logged-in");
      elements.loginRegisterButton.addEventListener("click", function () {
        localStorage.removeItem("token");
        window.location.reload();
      });
    } else {
      elements.loginRegisterButton.classList.remove("logged-in");
    }
  } else {
    elements.loginRegisterButton.classList.remove("logged-in");
  }
}

checkUserLoginStatus();
