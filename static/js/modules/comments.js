// Comment thread (templates/components/comments.html). Replaces blog.js + blog_apis.js string building.
// Server contract: GET <list>?page=N -> [{number, num_pages}, ...replies]; POST JSON <update><pk>/ {comment};
// create/delete are form posts that redirect back. Replies nest up to depth 3, like the server allows.
import { csrfFetch } from "../core.js";

const MAX_DEPTH = 3;
const PAGE_WINDOW = 10;

const section = document.querySelector("[data-comments]");
if (section) init(section);

function init(root) {
  const { listUrl, updateUrl, deleteUrl } = root.dataset;
  const list = root.querySelector("[data-comments-list]");
  const pages = root.querySelector("[data-comments-pages]");
  const status = root.querySelector("[data-comments-status]");
  const form = root.querySelector("[data-comment-form]");
  const commentTpl = root.querySelector("template[data-comment-tpl]");
  const editTpl = root.querySelector("template[data-edit-tpl]");
  const formHome = form?.parentNode;
  const formNext = form?.nextSibling;

  const fail = () => { status.textContent = root.dataset.tError; };

  async function load(page = 1) {
    try {
      const res = await fetch(`${listUrl}?page=${page}`, { credentials: "same-origin" });
      if (!res.ok) throw new Error(res.status);
      const [info, ...replies] = await res.json();
      resetForm();
      list.replaceChildren(...buildTree(replies));
      renderPages(info);
    } catch { fail(); }
  }

  // parent/child by pk; a reply whose parent is on another page is shown at the top level
  function buildTree(replies) {
    const nodes = new Map(replies.map((r) => [String(r.pk), { reply: r, el: renderComment(r) }]));
    const roots = [];
    for (const { reply, el } of nodes.values()) {
      const parent = nodes.get(String(reply.parent));
      if (parent) parent.el.querySelector(".c-comment__children").append(el);
      else roots.push(el);
    }
    return roots;
  }

  function renderComment(r) {
    const li = commentTpl.content.firstElementChild.cloneNode(true);
    const f = (name) => li.querySelector(`[data-f="${name}"]`);
    li.dataset.pk = r.pk;
    li.dataset.depth = r.depth;
    const avatar = f("avatar");
    avatar.addEventListener("error", () => avatar.remove(), { once: true });  // no broken-image icon
    if (r.thumbnail) avatar.src = r.thumbnail; else avatar.remove();
    f("author").textContent = r.author;
    f("time").textContent = r.created_at;
    f("comment").textContent = r.comment;
    f("delete").action = `${deleteUrl}${r.pk}/`;
    const mine = r.user_auth === true; // computed per request by the server, never cached
    li.querySelectorAll(":scope > article [data-own]").forEach((el) => { el.hidden = !mine; });
    return li;
  }

  function renderPages({ number, num_pages: last }) {
    pages.replaceChildren();
    if (!last || last < 2) return;
    const start = Math.max(1, Math.min(number - Math.floor(PAGE_WINDOW / 2), last - PAGE_WINDOW + 1));
    const end = Math.min(last, start + PAGE_WINDOW - 1);
    const nav = document.createElement("nav");
    nav.setAttribute("aria-label", root.dataset.tPages);
    const ul = document.createElement("ul");
    ul.className = "pagination";
    const item = (label, page, { current = false, disabled = false, aria } = {}) => {
      const li = document.createElement("li");
      li.className = "page-item" + (current ? " active" : "") + (disabled ? " disabled" : "");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "page-link";
      btn.textContent = label;
      btn.disabled = disabled;
      btn.dataset.page = page;
      if (aria) btn.setAttribute("aria-label", aria);
      if (current) btn.setAttribute("aria-current", "page");
      li.append(btn);
      ul.append(li);
    };
    item("‹", number - 1, { disabled: number <= 1, aria: root.dataset.tPrev });
    for (let p = start; p <= end; p++) item(String(p), p, { current: p === number });
    item("›", number + 1, { disabled: number >= last, aria: root.dataset.tNext });
    nav.append(ul);
    pages.append(nav);
  }

  // reply: move the one comment form under the target comment
  function startReply(li) {
    if (!form) return;
    const depth = Math.min(Number(li.dataset.depth) + 1, MAX_DEPTH);
    const author = li.querySelector('[data-f="author"]').textContent;
    form.elements.depth.value = depth;
    form.elements.parent.value = li.dataset.pk;
    const note = form.querySelector("[data-replying]");
    note.textContent = `${root.dataset.tReplying} ${author}`;
    note.hidden = false;
    form.querySelector('[data-action="cancel-reply"]').hidden = false;
    // deep replies keep the legacy "@author " prefix so the thread stays readable at the depth cap
    form.elements.comment.value = Number(li.dataset.depth) > 1 ? `@${author} ` : "";
    li.querySelector(":scope > article").after(form);
    form.elements.comment.focus();
  }

  function resetForm() {
    if (!form) return;
    form.elements.depth.value = 0;
    form.elements.parent.value = "";
    form.querySelector("[data-replying]").hidden = true;
    form.querySelector('[data-action="cancel-reply"]').hidden = true;
    formHome.insertBefore(form, formNext);
  }

  function startEdit(li) {
    const body = li.querySelector('[data-f="comment"]');
    if (body.hidden) return;
    const editor = editTpl.content.firstElementChild.cloneNode(true);
    editor.querySelector("textarea").value = body.textContent;
    body.hidden = true;
    body.after(editor);
    editor.querySelector("textarea").focus();
  }

  function endEdit(li, text) {
    const body = li.querySelector('[data-f="comment"]');
    if (text !== undefined) body.textContent = text;
    body.hidden = false;
    li.querySelector(".c-comment__edit")?.remove();
  }

  async function saveEdit(li) {
    const comment = li.querySelector(".c-comment__edit textarea").value.trim();
    if (!comment) return;
    try {
      const res = await csrfFetch(`${updateUrl}${li.dataset.pk}/`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment }) });
      if (!res.ok) throw new Error(res.status);
      endEdit(li, comment);
    } catch { fail(); }
  }

  root.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-action], [data-page]");
    if (!btn || !root.contains(btn)) return;
    const li = btn.closest(".c-comment");
    if (btn.dataset.page) return load(Number(btn.dataset.page));
    switch (btn.dataset.action) {
      case "reply": return startReply(li);
      case "cancel-reply": resetForm(); return form.elements.comment.focus();
      case "edit": return startEdit(li);
      case "edit-cancel": return endEdit(li);
      case "edit-save": return saveEdit(li);
    }
  });

  load();
}
