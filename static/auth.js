const authState = { mode: "signin" };

const signinTab = document.getElementById("signinTab");
const signupTab = document.getElementById("signupTab");
const authHeading = document.getElementById("authHeading");
const authSubtext = document.getElementById("authSubtext");
const authSubmit = document.getElementById("authSubmit");
const authMessage = document.getElementById("authMessage");

function setAuthMode(mode) {
  authState.mode = mode;
  const isSignin = mode === "signin";
  signinTab.classList.toggle("active", isSignin);
  signupTab.classList.toggle("active", !isSignin);
  authHeading.textContent = isSignin ? "Welcome back" : "Create your account";
  authSubtext.textContent = isSignin
    ? "Sign in to continue to your home page."
    : "Signup first, then login and continue to your home page.";
  authSubmit.textContent = isSignin ? "Login" : "Signup";
  authMessage.textContent = "";
  authMessage.className = "status-message";
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    },
    ...options,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || data.message || "Request failed.");
  }
  return data;
}

function showMessage(type, text) {
  authMessage.className = `status-message ${type}`;
  authMessage.textContent = text;
}

signinTab.addEventListener("click", () => setAuthMode("signin"));
signupTab.addEventListener("click", () => setAuthMode("signup"));

authSubmit.addEventListener("click", async () => {
  const login = document.getElementById("authLogin").value.trim();
  const password = document.getElementById("authPassword").value;

  try {
    if (authState.mode === "signup") {
      const data = await api("/api/signup", {
        method: "POST",
        body: JSON.stringify({ login, password }),
      });
      setAuthMode("signin");
      showMessage("success", data.message);
      return;
    }

    await api("/api/signin", {
      method: "POST",
      body: JSON.stringify({ login, password }),
    });
    window.location.href = "/home";
  } catch (error) {
    showMessage("error", error.message);
  }
});

setAuthMode("signin");
