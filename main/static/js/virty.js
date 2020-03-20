//define
function Jsonget(URL) {
  return $.ajax({
    type: 'GET',
    timeout: 10000,
    url: URL,
    dataType: 'json',
    contentType: "application/json",
  }).fail(function (XMLHttpRequest) {
    if (XMLHttpRequest.status == 401) {
      alert("401")
      location.href = '/login';
    }
  }).always(function (e) {
  });
}

//interface plus
$(function () {
  var minCount = 1;
  var maxCount = 6;
  $('#demo-plus').on('click', function () {
    var inputCount = $('#demo-area .unit').length;
    if (inputCount < maxCount) {
      var element = $('#demo-area .unit:last-child').clone(true);
      $('#demo-area .unit').parent().append(element);
    }
  });

  $('.demo-minus').on('click', function () {
    var inputCount = $('#demo-area .unit').length;
    if (inputCount > minCount) {
      $(this).parents('.unit').remove();
    }
  });

  $('#image-plus').on('click', function () {
    var inputCount = $('#image-list .unit').length;
    if (inputCount < maxCount) {
      var element = $('#image-list .unit:last-child').clone(true);
      $('#image-list .unit').parent().append(element);
    }
  });

  $('.image-minus').on('click', function () {
    var inputCount = $('#image-list .unit').length;
    if (inputCount > minCount) {
      $(this).parents('.unit').remove();
    }
  });
  
});

//node list
$(document).ready(function () {
  Jsonget('/api/sql/kvm_node.json').done(function (result) {
    data = result.ResultSet
    for (var i in data) {
      $('#node-list').append('<option value="' + data[i][0] + '">' + data[i][0] + '</option>');
    }
  })
});

//define option
$('#node-list').on('change', function () {
  var node = $('#node-list option:selected').val();

  $('#network-list').children().remove();
  Jsonget('/api/json/network/?node=' + node).done(function (result) {
    data = result.ResultSet;
    for (var i in data[1]) {
      $('#network-list').append('<option value="' + data[1][i]['name'] + '">' + data[1][i]['name'] + '</option>');
    }
  })

  $('#archive-list').children().remove();
  Jsonget('/api/json/archive/?node=' + node).done(function (result) {
    data = result.ResultSet;
    for (var i in data) {
      $('#archive-list').append('<option value="' + data[i]['name'] + '">' + data[i]['name'] + '</option>');
    }
  })

  $('#storage-list').children().remove();
  Jsonget('/api/json/storage/?node=' + node).done(function (result) {
    data = result.ResultSet;
    for (var i in data) {
      $('#storage-list').append('<option value="' + data[i]['name'] + '">' + data[i]['name'] + '</option>');
    }
  })
});

//table sort
$(document).ready(function () {
  $('.table').tablesorter();
});

///menu
$(document).ready(function () {
  $(".navbar-burger").click(function () {
    $(".navbar-burger").toggleClass("is-active");
    $(".navbar-menu").toggleClass("is-active");
  });
  $(".modal-delete").click(function () {
    $(".modal").removeClass("is-active");
  });
  $(".open-interface").click(function () {
    var mac = $(this).attr("id");
    $("#modal-mac").attr('value',mac);
    $("#modal-interface").addClass("is-active");
  });
  $("#modal-open-undefine").click(function () {
    $("#modal-undefine").addClass("is-active");
  });
});



///effect
$(document).ready(function () {
  $('.tabs ul li').each(function () {
    var $href = $(this).children('a').attr('href');
    var $path = location.pathname + location.search;
    if ($href == $path) {
      $(this).addClass('is-active');
    } else {
      $(this).removeClass('is-active');
    }
  });
  $('.menu li a').each(function () {
    var $href = $(this).attr('href');
    if (location.pathname.match($href)) {
      $(this).addClass('is-active');
    } else {
      $(this).removeClass('is-active');
    }
  });
});