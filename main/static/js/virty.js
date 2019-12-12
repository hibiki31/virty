var minCount = 1;
var maxCount = 6;

$(function () {
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
});

$(function () {
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



$(function () {
  $.getJSON('/api/sql/kvm_node.json', function (data) {
    for (var domain in data.ResultSet) {
      $('#node-list').append('<option value="' + data.ResultSet[domain][0] + '">' + data.ResultSet[domain][0] + '</option>');
    }
  });
});

$('#node-list').on('change', function () {
  var node = $('#node-list option:selected').val();

  $('#network-list').children().remove();
  $.getJSON('/api/json/network/?node=' + node, function (data) {
    for (var domain in data.ResultSet[0]) {
      $('#network-list').append('<option value="' + data.ResultSet[0][domain] + '">Interface ' + data.ResultSet[0][domain] + '</option>');
    }
    for (var domain in data.ResultSet[1]) {
      $('#network-list').append('<option value="' + data.ResultSet[1][domain]['bridge'] + '">Network ' + data.ResultSet[1][domain]['name'] + ' @' + data.ResultSet[1][domain]['bridge'] + '</option>');
    }
  });
  $('#image-json').children().remove();
  $.getJSON('/image/list', function (data) {
    for (var domain in data.ResultSet) {
      if (data.ResultSet[domain][2] == node) {
        $('#image-json').append('<option value="' + data.ResultSet[domain][1] + '">' + data.ResultSet[domain][0] + ' src ' + data.ResultSet[domain][1] + '</option>');
      }
    }
  });
  $('#archive-list').children().remove();
  $.getJSON('/api/json/archive/?node=' + node, function (data) {
    for (var domain in data.ResultSet) {

      $('#archive-list').append('<option value="' + data.ResultSet[domain]['name'] + '">' + data.ResultSet[domain]['name'] + '</option>');

    }
  });
  $('#storage-list').children().remove();
  $.getJSON('/api/json/storage/?node=' + node, function (data) {
    for (var domain in data.ResultSet) {

      $('#storage-list').append('<option value="' + data.ResultSet[domain]['name'] + '">' + data.ResultSet[domain]['name'] + '</option>');

    }
  });
});



$(function () {
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
  }, 500);
});


$(document).ready(function () {
  $('[id$=table]').tablesorter();
});

$.ajaxSetup({
  headers: {
    'Authorization': 'JWT' + $.cookie('access_token')
  }
})