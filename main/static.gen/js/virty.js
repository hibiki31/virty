$(document).ready(function () {
  $(".navbar-burger").click(function () {
    $(".navbar-burger").toggleClass("is-active");
    $(".navbar-menu").toggleClass("is-active");
  });
});
$(function () {
  $('.menu li a').each(function () {
    var $href = $(this).attr('href');
    if (location.pathname.match($href)) {
      $(this).addClass('is-active');
    } else {
      $(this).removeClass('is-active');
    }
  });
});
$('td').hover(
  function () {
    $(this).addClass('is-active');
  },
  function () {
    $(this).removeClass('is-active');
  }
);