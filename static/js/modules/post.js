// Blog post page: like toggle and the once-per-browser visit count. Replaces the blog_apis.js parts.
import { csrfFetch } from "../core.js";

const like = document.querySelector("[data-like-url]");
like?.addEventListener("click", async () => {
  if (like.dataset.loginUrl) { location.href = like.dataset.loginUrl; return; }  // anonymous: the view needs a login
  like.disabled = true;
  try {
    const res = await csrfFetch(like.dataset.likeUrl, { method: "POST" });
    if (!res.ok) throw new Error(res.status);
    const { like_count } = await res.json();
    const on = like.getAttribute("aria-pressed") !== "true";
    like.setAttribute("aria-pressed", String(on));
    like.querySelector("[data-like-count]").textContent = like_count;
  } catch { /* leave the button as it was */ } finally { like.disabled = false; }
});

const visit = document.querySelector("[data-visit-url]");
if (visit) {
  const key = `visit:${location.pathname}`;
  let seen = null;
  try { seen = localStorage.getItem(key); } catch { /* storage blocked: count every visit */ }
  if (!seen) {
    fetch(visit.dataset.visitUrl, { credentials: "same-origin" })
      .then((res) => { if (res.ok) try { localStorage.setItem(key, "1"); } catch { /* ignore */ } })
      .catch(() => {});
  }
}
