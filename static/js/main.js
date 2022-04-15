(function() {
    
    "use strict";
    
    //===== Prealoder

    window.onload = function() {
        window.setTimeout(fadeout, 500);
    }

    function fadeout() {
        document.querySelector('.preloader').style.opacity = '0';
        document.querySelector('.preloader').style.display = 'none';
    }

    /*=====================================
    Sticky
    ======================================= */
    window.onscroll = function () {
        var header_navbar = document.getElementById("header_navbar");
        var sticky = header_navbar.offsetTop;
        // var logo = document.querySelector('.navbar-brand img')

        if (window.pageYOffset > sticky) {
            header_navbar.classList.add("sticky");
            // logo.src = 'assets/images/logo/logo-2.svg';
        } else {
            header_navbar.classList.remove("sticky");
            // logo.src = 'assets/images/logo/logo.svg';
        }



        // show or hide the back-top-top button
        var backToTo = document.querySelector(".back-to-top");
        if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
            backToTo.style.display = "block";
        } else {
            backToTo.style.display = "none";
        }
    };

    //WOW Scroll Spy
    var wow = new WOW({
        //disabled for mobile
        mobile: false
    });
    wow.init();


    /*---canvas menu activation---*/

    const canvasToggler = document.querySelector(".canvas_open");
    const offcanvasMenuToggler = document.querySelector(".offcanvas_menu_wrapper");
    const bodyOverlayToggler = document.querySelector(".body_overlay");
    const canvasCloseToggler = document.querySelector(".canvas_close");

    canvasToggler.addEventListener('click', function() {
        console.log('canvas_open');
        bodyOverlayToggler.classList.add("active");
        offcanvasMenuToggler.classList.add("active");
    }) 

    canvasCloseToggler.addEventListener('click', function() {
        offcanvasMenuToggler.classList.remove("active");
        bodyOverlayToggler.classList.remove("active");
    }) 

    bodyOverlayToggler.addEventListener('click', function() {
        offcanvasMenuToggler.classList.remove("active");
        bodyOverlayToggler.classList.remove("active");
    })

    //========= glightbox
		/*const myGallery = GLightbox({
			'href': 'assets/video/Free App Landing Page Template - AppLand.mp4',
			'type': 'video',
			'source': 'youtube', //vimeo, youtube or local
			'width': 900,
			'autoplayVideos': true,
		});*/

    //======== tiny slider for portfolio-product-carousel 
    tns({
        slideBy: 'page',
        autoplay: false,
        mouseDrag: true,
        gutter: 20,
        nav: false,
        controls: true,
        controlsPosition: 'bottom',
        controlsText: [
            '<span class="prev"><i class="lni lni-chevron-left"></i></span>', 
            '<span class="next"><i class="lni lni-chevron-right"></i></span>'
        ],
        container: ".portfolio-product-carousel",
        items: 1,
        center: false,
        autoplayTimeout: 5000,
        swipeAngle: false,
        speed: 400,
        responsive: {
            768: {
                items: 1,
            },

            992: {
                items: 1,
            },

            1200: {
                items: 1,
            }
        }
    });

    //======== tiny slider for analyze-product-carousel
		// tns({
		// 	slideBy: 'page',
		// 	autoplay: false,
		// 	mouseDrag: true,
		// 	gutter: 20,
		// 	nav: false,
		// 	controls: true,
		// 	controlsPosition: 'bottom',
		// 	controlsText: [
		// 		'<span class="prev"><i class="lni lni-chevron-left"></i></span>', 
		// 		'<span class="next"><i class="lni lni-chevron-right"></i></span>'
		// 	],
		// 	container: ".analyze-product-carousel",
		// 	items: 1,
		// 	center: false,
		// 	autoplayTimeout: 5000,
		// 	swipeAngle: false,
		// 	speed: 400,
		// 	responsive: {
		// 		768: {
		// 			items: 2,
		// 		},

		// 		992: {
		// 			items: 2,
		// 		},

		// 		1200: {
		// 			items: 3,
		// 		}
		// 	}
		// });       

    //AOS Scroll 
    AOS.init({
        once: true,
    });

})();