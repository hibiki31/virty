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
  $('#interface-op-add').on('click', function () {
    var inputCount = $('#define-interface .unit').length;
    if (inputCount < maxCount) {
      var element = $('#define-interface .unit:last-child').clone(true);
      $('#define-interface .unit').parent().append(element);
    }
  });

  $('.interface-op-remove').on('click', function () {
    var inputCount = $('#define-interface .unit').length;
    if (inputCount > minCount) {
      $(this).parents('.unit').remove();
    }
  });
});

//define option
$('#node-list').on('change', function () {
  var node = $('#node-list option:selected').val();

  $('.network-list').children().remove();
  Jsonget('/api/json/network/?node=' + node).done(function (result) {
    data = result.ResultSet;
    for (var i in data[1]) {
      $('.network-list').append('<option value="' + data[1][i]['name'] + '">' + data[1][i]['name'] + '</option>');
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
    $("#modal-mac").attr('value', mac);
    $("#modal-interface").addClass("is-active");
  });

  $("#modal-open-undefine").click(function () {
    $("#modal-undefine").addClass("is-active");
  });

  $(".modal-open-group").click(function () {
    $("#modal-group-id").attr('value', $(this).attr("groupid"));
    $("#modal-user-id").attr('value', $(this).attr("userid"));
    $("#modal-group").addClass("is-active");
  });

  $(".modal-open-domain-user").click(function () {
    $("#modal-open-user").addClass("is-active");
    $("#modal-uuid-user").attr('value', $(this).attr("uuid"));
  });

  $(".modal-open-domain-group").click(function () {
    $("#modal-open-group").addClass("is-active");
    $("#modal-uuid-group").attr('value', $(this).attr("uuid"));
  });

  $(".modal-open-image-delete").click(function () {
    $("#modal-image-node").attr('value', $(this).parent().siblings('td[name="node"]').attr("value"));
    $("#modal-image-pool").attr('value', $(this).parent().siblings('td[name="pool"]').attr("value"));
    $("#modal-image-name").attr('value', $(this).parent().siblings('td[name="name"]').attr("value"));
    $("#modal-open-image-delete").addClass("is-active");
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
  $('tbody tr').hover(function () {
    $(this).addClass("is-selected");
  }, function () {
    $(this).removeClass("is-selected");
  });
});