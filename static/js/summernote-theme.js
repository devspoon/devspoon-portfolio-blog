// Summernote editor iframe: mirror the parent page's theme and colour tokens (same origin), and follow the
// theme toggle. Colours are read from the parent's tokens, so no colour values live here (INV-1).
(function () {
  var TOKENS = ["--c-bg", "--c-surface", "--c-surface-2", "--c-text", "--c-text-muted", "--c-line"];
  var root = document.documentElement;

  function sync() {
    try {
      var parentRoot = window.parent.document.documentElement;
      var style = window.parent.getComputedStyle(parentRoot);
      root.dataset.theme = parentRoot.dataset.bsTheme === "dark" ? "dark" : "light";
      TOKENS.forEach(function (name) { root.style.setProperty(name, style.getPropertyValue(name)); });
    } catch (e) { /* opened outside the post form: keep Summernote's light look */ }
  }

  sync();
  try {
    new MutationObserver(sync).observe(window.parent.document.documentElement,
      { attributes: true, attributeFilter: ["data-bs-theme"] });
  } catch (e) { /* no parent page */ }
})();
