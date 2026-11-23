// Site-wide behaviour loaded on every page (ES module). Page features live in js/modules/*.

const root = document.documentElement;

// theme: the inline script in <head> applies the saved/OS theme before paint; this only toggles it
document.addEventListener("click", (event) => {
  const toggle = event.target.closest("[data-theme-toggle]");
  if (!toggle) return;
  const next = root.dataset.bsTheme === "dark" ? "light" : "dark";
  root.dataset.bsTheme = next;
  try { localStorage.setItem("theme", next); } catch { /* private mode: theme just isn't remembered */ }
});

// header: when the menu does not fit next to the tools (many or long entries), it moves to a second row
const siteNav = document.querySelector(".site-nav");
if (siteNav && "ResizeObserver" in window) {
  const fit = () => {
    siteNav.classList.remove("is-compact");
    siteNav.classList.toggle("is-compact", siteNav.scrollWidth > siteNav.clientWidth + 1);
  };
  const observer = new ResizeObserver(fit);
  observer.observe(siteNav);
  observer.observe(siteNav.querySelector(".navbar-nav")); // web fonts arriving change its width only
}

// <select data-autosubmit> (language switch) submits its form on change; <noscript> keeps a button
document.addEventListener("change", (event) => {
  if (event.target.matches("select[data-autosubmit]")) event.target.form.requestSubmit();
});

// fetch with Django's CSRF header, for POST/DELETE from page modules
export function csrfFetch(url, options = {}) {
  const token = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)?.[1] ?? "";
  return fetch(url, { credentials: "same-origin", ...options,
    headers: { "X-CSRFToken": token, "X-Requested-With": "XMLHttpRequest", ...(options.headers ?? {}) } });
}
