function Jsonget(URL) {
  return $.ajax({
    type: 'GET',
    timeout: 10000,
    url: URL,
    dataType: 'json',
    contentType: "application/json",
  }).fail(function (XMLHttpRequest) {
    if (XMLHttpRequest.status == 401) {
      location.href = '/login';
    }
  }).always(function (e) {
  });
}

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

// Node list
$(function () {
  Jsonget('/api/sql/kvm_node.json').done(function (result) {
    data = result.ResultSet
    for (var i in data) {
      $('#node-list').append('<option value="' + data[i][0] + '">' + data[i][0] + '</option>');
    }
  })
});

// Define Option
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




// Queue
$(function () {
  Jsonget('/ui/get/info').done(function (result) {
    $('.user_id').text(result.user_id);
  })

  setInterval(function () {
    $.getJSON('/api/json/stack-que', function (data) {
      let p = 0;
      for (let i in data.ResultSet) {
        if ($('#que-status li > a').length <= p) {
          let add_contents = '<li><a><span class="image"><img src="/static/images/admiral.jpg" alt="Profile Image" /></span>'
          add_contents += '<span><span class="quename">' + data.ResultSet[i][4] + '</span><span class="time">' + data.ResultSet[i][1] + '</span></span><span class="message"></span></a></li>'
          $('#que-status').prepend(add_contents);
        } else {
          $('#que-status .quename').eq(p).text(data.ResultSet[i][4]);
          $('#que-status .time').eq(p).text(data.ResultSet[i][1]);
        }
        p++;
      }
      $('#que-status').children(':not(:last-child):nth-child(n + ' + (p + 1) + ')').remove();

      $('#que-badge').html(data.ResultSet.length)
      if (data.ResultSet.length == 0) {
        $('#que-badge').hide();
      } else {
        $('#que-badge').show();
      }
    });
  }, 10000);
});

// Table sort
$(document).ready(function () {
  $('.table').tablesorter();
});



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