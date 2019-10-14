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