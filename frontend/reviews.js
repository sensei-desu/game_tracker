
"use strict";

const API_BASE = "https://game-tracker-19sp.onrender.com";
const $ = (id) => document.getElementById(id);

let accessToken = null;
let username = null;
let userId = null;
let selectedRating = 0;
let editingReview = false;
let reviews = [];
let authMode = "login";

const cats = { 1: "😿", 2: "🙀", 3: "🐱", 4: "😺", 5: "😻" };

function message(id, text, type = "") {
  const el = $(id);
  el.textContent = text;
  el.className = `form-message ${type}`.trim();
  el.hidden = !text;
}

async function api(path, options = {}) {
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const raw = await response.text();
  let data = {};

  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    throw new Error("The server returned an invalid response.");
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Request failed (${response.status}).`
    );
  }

  return data;
}

function showAuth(mode = "login") {
  authMode = mode;
  $("authSection").hidden = false;
  $("reviewFormSection").hidden = true;
  $("authTitle").textContent =
    mode === "signup" ? "Create your account" : "Welcome back";
  $("authDescription").textContent =
    mode === "signup"
      ? "Choose a username and password to join the community."
      : "Log in to write or edit your review.";
  $("authSubmitButton").textContent =
    mode === "signup" ? "Create account" : "Log in";
  $("loginTab").classList.toggle("active", mode === "login");
  $("signupTab").classList.toggle("active", mode === "signup");
  $("loginTab").setAttribute("aria-selected", String(mode === "login"));
  $("signupTab").setAttribute("aria-selected", String(mode === "signup"));
  $("authPassword").autocomplete =
    mode === "signup" ? "new-password" : "current-password";
  message("authMessage", "");
  $("authSection").scrollIntoView({ behavior: "smooth", block: "center" });
}

function updateAccount() {
  const loggedIn = Boolean(accessToken && username);
  $("accountStatus").textContent = loggedIn
    ? `Signed in as ${username}`
    : "Browsing as guest";
  $("navLogin").hidden = loggedIn;
  $("navSignup").hidden = loggedIn;
  $("logoutButton").hidden = !loggedIn;
}

function chooseRating(value) {
  selectedRating = Number(value) || 0;
  document.querySelectorAll(".cat-choice").forEach((button) => {
    const active = Number(button.dataset.rating) === selectedRating;
    button.classList.toggle("selected", active);
    button.setAttribute("aria-checked", String(active));
  });
  $("ratingHint").textContent = selectedRating
    ? `${cats[selectedRating]} You selected ${selectedRating} out of 5 stars.`
    : "Choose your cat rating.";
}

function showReviewForm(review = null) {
  if (!accessToken) {
    showAuth("login");
    message("authMessage", "Log in to continue writing a review.");
    return;
  }

  editingReview = Boolean(review);
  $("authSection").hidden = true;
  $("reviewFormSection").hidden = false;
  $("reviewFormTitle").textContent = review ? "Edit your review" : "Write your review";
  $("submitReviewButton").textContent = review ? "Save changes" : "Publish review";
  $("reviewText").value = review?.review_text || "";
  $("characterCount").textContent = `${$("reviewText").value.length} / 1000`;
  chooseRating(review?.rating || 0);
  message("reviewFormMessage", "");
  $("reviewFormSection").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function handleAuth(event) {
  event.preventDefault();

  const name = $("authUsername").value.trim().toLowerCase();
  const password = $("authPassword").value;

  if (!/^[a-z0-9_]{3,20}$/.test(name)) {
    message("authMessage", "Use 3–20 letters, numbers, or underscores.", "error");
    return;
  }
  if (password.length < 6) {
    message("authMessage", "Password must be at least 6 characters.", "error");
    return;
  }

  const button = $("authSubmitButton");
  button.disabled = true;
  button.textContent = "Please wait…";

  try {
    const data = await api(`/api/auth/${authMode}`, {
      method: "POST",
      body: JSON.stringify({ username: name, password }),
    });

    if (!data.access_token || !data.user?.id) {
      throw new Error("No valid session was returned.");
    }

    accessToken = data.access_token;
    username = data.user.username || name;
    userId = data.user.id;
    $("authForm").reset();
    updateAccount();
    $("authSection").hidden = true;

    await loadReviews();
    const ownReview = reviews.find((review) => review.user_id === userId);
    showReviewForm(ownReview || null);
  } catch (error) {
    message("authMessage", error.message, "error");
  } finally {
    button.disabled = false;
    button.textContent = authMode === "signup" ? "Create account" : "Log in";
  }
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderReviews() {
  const list = $("reviewsList");
  list.replaceChildren();

  $("reviewCount").textContent = String(reviews.length);
  const avg = reviews.length
    ? reviews.reduce((sum, item) => sum + Number(item.rating), 0) / reviews.length
    : 0;
  $("averageRating").textContent = reviews.length ? avg.toFixed(1) : "—";

  if (!reviews.length) {
    list.append(element("div", "empty-reviews",
      "No reviews yet. Be the first to share your experience!"));
    $("reviewsMessage").textContent = "";
    return;
  }

  $("reviewsMessage").textContent = "";

  reviews.forEach((review) => {
    const rating = Math.max(1, Math.min(5, Number(review.rating) || 1));
    const card = element("article", "review-card");
    const top = element("div", "review-card-top");
    const identity = element("div", "reviewer-identity");
    identity.append(element("div", "reviewer-avatar", "🐾"));

    const info = element("div");
    info.append(element("div", "reviewer-name", review.username || "Player"));
    const date = new Date(review.created_at);
    info.append(element("span", "review-date",
      Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString()));
    identity.append(info);

    const stars = element("div", "review-rating",
      "★".repeat(rating) + "☆".repeat(5 - rating));
    top.append(identity, stars);
    card.append(top, element("div", "review-cat", cats[rating]),
      element("p", "review-text", review.review_text || ""));

    if (userId && review.user_id === userId) {
      const actions = element("div", "review-card-actions");
      const edit = element("button", "button button-quiet", "Edit my review");
      edit.type = "button";
      edit.addEventListener("click", () => showReviewForm(review));
      actions.append(edit);
      card.append(actions);
    }
    list.append(card);
  });
}

async function loadReviews() {
  $("reviewsMessage").textContent = "Loading reviews…";
  $("refreshReviewsButton").disabled = true;

  try {
    reviews = await api("/api/reviews");
    renderReviews();
  } catch (error) {
    $("reviewsMessage").textContent = `Couldn't load reviews: ${error.message}`;
  } finally {
    $("refreshReviewsButton").disabled = false;
  }
}

async function submitReview(event) {
  event.preventDefault();

  if (!accessToken) {
    showAuth("login");
    return;
  }
  if (!selectedRating) {
    message("reviewFormMessage", "Choose a cat rating first.", "error");
    return;
  }

  const reviewText = $("reviewText").value.trim();
  if (reviewText.length < 10 || reviewText.length > 1000) {
    message("reviewFormMessage", "Review must contain 10–1000 characters.", "error");
    return;
  }

  const button = $("submitReviewButton");
  button.disabled = true;

  try {
    if (editingReview) {
      throw new Error("Editing needs a review-update endpoint on the backend; new review submissions work.");
    }

    await api("/api/reviews", {
      method: "POST",
      body: JSON.stringify({ rating: selectedRating, review_text: reviewText }),
    });

    $("reviewForm").reset();
    $("characterCount").textContent = "0 / 1000";
    chooseRating(0);
    $("reviewFormSection").hidden = true;
    await loadReviews();
  } catch (error) {
    message("reviewFormMessage", error.message, "error");
  } finally {
    button.disabled = false;
    button.textContent = editingReview ? "Save changes" : "Publish review";
  }
}

function logout() {
  accessToken = null;
  username = null;
  userId = null;
  editingReview = false;
  updateAccount();
  $("reviewFormSection").hidden = true;
  $("authSection").hidden = true;
  renderReviews();
}

function initialize() {
  $("navLogin").addEventListener("click", () => showAuth("login"));
  $("navSignup").addEventListener("click", () => showAuth("signup"));
  $("logoutButton").addEventListener("click", logout);
  $("writeReviewButton").addEventListener("click", () => {
    if (!accessToken) return showAuth("login");
    const ownReview = reviews.find((review) => review.user_id === userId);
    showReviewForm(ownReview || null);
  });

  $("loginTab").addEventListener("click", () => showAuth("login"));
  $("signupTab").addEventListener("click", () => showAuth("signup"));
  $("closeAuthButton").addEventListener("click", () => {
    $("authSection").hidden = true;
  });
  $("cancelReviewButton").addEventListener("click", () => {
    $("reviewFormSection").hidden = true;
  });

  $("authForm").addEventListener("submit", handleAuth);
  $("reviewForm").addEventListener("submit", submitReview);
  $("refreshReviewsButton").addEventListener("click", loadReviews);
  $("reviewText").addEventListener("input", () => {
    $("characterCount").textContent = `${$("reviewText").value.length} / 1000`;
  });

  document.querySelectorAll(".cat-choice").forEach((button) => {
    button.addEventListener("click", () => chooseRating(button.dataset.rating));
  });

  updateAccount();
  chooseRating(0);
  loadReviews();
}

document.addEventListener("DOMContentLoaded", initialize);
