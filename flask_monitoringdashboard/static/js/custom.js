(function ($) {
    "use strict";
    // Configure tooltips for collapsed side navigation
    $('.navbar-sidenav [data-toggle="tooltip"]').tooltip({
        template: '<div class="tooltip navbar-sidenav-tooltip" role="tooltip" style="pointer-events: none;"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
    })
    // Toggle the side navigation
    $("#sidenavToggler").click(function (e) {
        e.preventDefault();
        $("body").toggleClass("sidenav-toggled");
        $(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
        $(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
    });
    // Force the toggled class to be removed when a collapsible nav link is clicked
    $(".navbar-sidenav .nav-link-collapse").click(function (e) {
        e.preventDefault();
        $("body").removeClass("sidenav-toggled");
    });
    // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
    $('body.fixed-nav .navbar-sidenav, body.fixed-nav .sidenav-toggler, body.fixed-nav .navbar-collapse').on('mousewheel DOMMouseScroll', function (e) {
        var e0 = e.originalEvent,
            delta = e0.wheelDelta || -e0.detail;
        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
    });
    // Scroll to top button appear
    $(document).scroll(function () {
        var scrollDistance = $(this).scrollTop();
        if (scrollDistance > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });
    // Configure tooltips globally
    $('[data-toggle="tooltip"]').tooltip()
    // Smooth scrolling using jQuery easing
    $(document).on('click', 'a.scroll-to-top', function (event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top)
        }, 1000, 'easeInOutExpo');
        event.preventDefault();
    });

    // update to hide everying of hide-tag
    $("hide").text("");

    // update the duration of every html-time tag
    $("time").text(function(i, ms){
        // ms is a float or int
        //ms = Math.round(parseFloat(ms) / 10) * 10;
        ms = Math.round( parseFloat(ms) * 10) / 10;
        var s = ms / 1000;
        var min = Math.floor(s / 60);
        var hr = Math.floor(s / 3600);
        var day = Math.floor(hr / 24);
        var value = "";
        if (ms < 100.5){
            value = ms + " ms";
        } else if (ms < 999.5){
            value = Math.round(ms) + " ms";
        } else if (s < 60){
            s = Math.round(ms / 100) / 10;
            value = s + " sec";
        } else if (hr == 0){
            s = Math.round(s % 60);
            value = min + " min";
            if (s > 0){
                value += ", " + s + " sec";
            }
        } else if (day == 0){
            value = hr + " hr";
            min = Math.round(min % 60);
            if (min > 0){
                value += ", " + min + " min";
            }
        } else {
           value = day + " d";
           hr = Math.round(hr % 24);
           if (hr > 0){
               value += ", " + hr + " hr";
           }
        }
        return value;
    });
})(jQuery);