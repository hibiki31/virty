//////////////////////////////
///    function            ///
//////////////////////////////
function Jsonget(URL) {
  return $.ajax({
    type: 'GET',
    timeout: 10000,
    url: URL,
    dataType: 'json',
    contentType: "application/json",
  }).fail(function (XMLHttpRequest) {
    if (XMLHttpRequest.status == 401) {
      alert("401");
      location.href = '/login';
    }
  }).always(function (e) {
  });
}





//////////////////////////////
///    loading             ///
//////////////////////////////
$(document).ready(function () {
  $("#domain-reload").click(function () {
    $(this).addClass("is-loading");
    $.post("/api/que/domain/list-reload", { "select": "all", "return": "json" }, function (dt) {
      console.log(JSON.stringify(dt));
      $.ajax({
        url: '/queue/status/' + dt['que-id'][0],
        type: 'GET',
        timeout: 10000,
        contentType: "json",
        data: {
          'interval': 10000
        }
      }).done((data) => {
      }).fail((data) => {
      }).always((data) => {
        $(".is-loading").removeClass("is-loading");
        location.href = '/';
      });
    });
  });
});

$(document).ready(function () {
  $("#modal-open-image-delete-button").click(function () {
    $(this).addClass("is-loading");
    $.post("/api/que/image/delete", {
      "node": $("#modal-image-node").attr('value'),
      "pool": $("#modal-image-pool").attr('value'),
      "name": $("#modal-image-name").attr('value'),
      "status": "delete",
      "return": "json"
    }, function (dt) {
      $.ajax({
        url: '/queue/status/' + dt,
        type: 'GET',
        timeout: 10000,
        contentType: "json",
        data: {
          'interval': 10000
        }
      }).done((data) => {
      }).fail((data) => {
      }).always((data) => {
        $(".is-loading").removeClass("is-loading");
        location.reload();
      });
    });

  });
});





//////////////////////////////
///    interface plus      ///
//////////////////////////////
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





//////////////////////////////
///    define option       ///
//////////////////////////////
$('#node-list').on('change', function () {
  var node = $('#node-list option:selected').val();

  $('.network-list').children().remove();
  $('#archive-list').children().remove();
  $('#storage-list').children().remove();

  Jsonget('/domain/define?json=define&node=' + node).done(function (result) {
    $.each(result['network'][0], function (index, value) {
      $('.network-list').append('<option value="' + value + '">' + value + '</option>');
    });
    $.each(result['archive'], function (index, value) {
      $('#archive-list').append('<option value="' + value[0] + '">' + value[0] + '</option>');
    });
    $.each(result['storage'], function (index, value) {
      $('#storage-list').append('<option value="' + value['name'] + '">' + value['name'] + '</option>');
    });
  })
});

$('#list-type').on('change', function () {
  var type = $('#list-type option:selected').val();
  if (type === "archive") {
    $('#step-2-archive').show();
    $('#step-2-empty').hide();
    $('#step-2-img').hide();
    $('#input-size').removeAttr('required');
  } else if (type === "empty") {
    $('#step-2-archive').hide();
    $('#step-2-empty').show();
    $('#step-2-img').hide();
    $('#input-size').attr('required');
  } else if (type === "img") {
    $('#step-2-archive').hide();
    $('#step-2-empty').hide();
    $('#step-2-img').show();
    $('#input-size').removeAttr('required');
  }
});



//////////////////////////////
///    table sort          ///
//////////////////////////////
$(document).ready(function () {
  $('.table').tablesorter();
});




//////////////////////////////
///    menu                ///
//////////////////////////////
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



  $(".modal-open").click(function () {
    $("#" + $(this).attr("modal-id")).addClass("is-active");
    
    if ($(this).attr("modal-id") === "modal-user-delete") {
      $(".modal-user-id").attr('value', $(this).attr("user-id"));
    }
    if ($(this).attr("modal-id") === "modal-user-reset") {
      $(".modal-user-id").attr('value', $(this).attr("user-id"));
    }
    if ($(this).attr("modal-id") === "modal-group-delete") {
      $(".modal-group-id").attr('value', $(this).attr("group-id"));
    }
    if ($(this).attr("modal-id") === "modal-group-assgin") {
      $(".modal-group-id").attr('value', $(this).attr("group-id"));
    }
    if ($(this).attr("modal-id") === "modal-archive-assign") {
      $(".modal-image-node").attr('value', $(this).attr("image-node"));
      $(".modal-image-pool").attr('value', $(this).attr("image-pool"));
      $(".modal-image-name").attr('value', $(this).attr("image-name"));
    }
  });

});





//////////////////////////////
///    effect              ///
//////////////////////////////
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
    if (location.pathname === $href) {
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