$(function(){
    setInterval(function(){
        $.getJSON('/api/sql/kvm_que.json', function(data) {
            for (var domain in data.ResultSet){
                $('#node-list').append('<option value="'+data.ResultSet[domain][0]+'">'+data.ResultSet[domain][0]+'</option>');
            }
        });
    },3000);
});