"use strict";
// GrayGrids theme behaviour: sticky header, back-to-top, preloader, off-canvas menu, AOS/WOW.
// Every element and library is optional, so a page without one (or a failed CDN) still works.

const headerNavbar = document.getElementById("header_navbar");
const backToTop = document.querySelector(".back-to-top");

window.addEventListener("scroll", function () {
    if (headerNavbar) headerNavbar.classList.toggle("sticky", window.pageYOffset > headerNavbar.offsetTop);
    if (backToTop) backToTop.style.display = document.documentElement.scrollTop > 50 ? "block" : "none";
});

// preloader: hidden on load; custom.css also hides it after a few seconds if this never runs
window.addEventListener("load", function () {
    window.setTimeout(function () {
        const preloader = document.querySelector(".preloader");
        if (preloader) preloader.style.display = "none";
    }, 500);
});

// off-canvas mobile menu
const canvasOpen = document.querySelector(".canvas_open");
const offcanvasMenu = document.querySelector(".offcanvas_menu_wrapper");
const bodyOverlay = document.querySelector(".body_overlay");
const canvasClose = document.querySelector(".canvas_close");

function setMenu(open) {
    if (!offcanvasMenu || !bodyOverlay) return;
    offcanvasMenu.classList.toggle("active", open);
    bodyOverlay.classList.toggle("active", open);
    if (canvasOpen) canvasOpen.querySelector("[aria-expanded]")?.setAttribute("aria-expanded", String(open));
}

canvasOpen?.addEventListener("click", function (event) { event.preventDefault(); setMenu(true); });
canvasClose?.addEventListener("click", function (event) { event.preventDefault(); setMenu(false); });
bodyOverlay?.addEventListener("click", function () { setMenu(false); });
document.addEventListener("keydown", function (event) { if (event.key === "Escape") setMenu(false); });

if (window.AOS) AOS.init({ once: false });
if (window.WOW) new WOW({ mobile: false }).init();
