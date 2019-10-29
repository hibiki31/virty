var minCount = 1;
var maxCount = 6;

$(function(){
$('#demo-plus').on('click', function(){
    var inputCount = $('#demo-area .unit').length;
    if (inputCount < maxCount){
        var element = $('#demo-area .unit:last-child').clone(true);
        $('#demo-area .unit').parent().append(element);
    }
});

$('.demo-minus').on('click', function(){
    var inputCount = $('#demo-area .unit').length;
    if (inputCount > minCount){
    $(this).parents('.unit').remove();
    }
});
});

$(function() {
    $.getJSON('/api/sql/kvm_node.json', function(data) {
        for (var domain in data.ResultSet){
            $('#node-list').append('<option value="'+data.ResultSet[domain][0]+'">'+data.ResultSet[domain][0]+'</option>');
        }
    });
});

$('#node-list').on('change', function() {
    $('#network-list').children().remove();
        var node = $('#node-list option:selected').val();
        $.getJSON('/api/sql/kvm_network.json', function(data) {
        for (var domain in data.ResultSet){
            if (data.ResultSet[domain][2] == node){
                $('#network-list').append('<option value="'+data.ResultSet[domain][1]+'">'+data.ResultSet[domain][0]+' src '+data.ResultSet[domain][1]+'</option>');
            }
        }
    });
});

$('#node-list').on('change', function() {
    $('#archive-list').children().remove();
        var node = $('#node-list option:selected').val();
        $.getJSON('/api/sql/kvm_archive.json', function(data) {
        for (var domain in data.ResultSet){
            if (data.ResultSet[domain][2] == node){
                $('#archive-list').append('<option value="'+data.ResultSet[domain][0]+'">'+data.ResultSet[domain][0]+'</option>');
            }
        }
    });
});

$(function() {
  setInterval(function() {
    $.getJSON('/api/getque.json', function(data) {
      let p = 0;
      for (let i in data.ResultSet) {
        if ($('#que-status li > a').length <= p) {
          let add_contents = '<li><a><span class="image"><img src="/static/images/admiral.jpg" alt="Profile Image" /></span>'
          add_contents += '<span><span class="quename">'+data.ResultSet[i][4]+'</span><span class="time">'+data.ResultSet[i][1]+'</span></span><span class="message"></span></a></li>'
          $('#que-status').prepend(add_contents);
        } else {
          $('#que-status .quename').eq(p).text(data.ResultSet[i][4]);
          $('#que-status .time').eq(p).text(data.ResultSet[i][1]);
        }
        p++;
      }
      $('#que-status').children(':not(:last-child):nth-child(n + '+(p+1)+')').remove();

      $('#que-badge').html(data.ResultSet.length)
      if (data.ResultSet.length == 0){
        $('#que-badge').hide();
      }else{
        $('#que-badge').show();
      }
    });
  },500);
});
  

$(document).ready(function() {
  $('[id$=table]').tablesorter();
});
