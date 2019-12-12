$(function () {
    $('#login').on('click', function () {
        console.log("data");
        $.ajax({
            url: '/auth',
            type: 'POST',
            data: JSON.stringify({
                'username': $('#userid').val(),
                'password': $('#password').val()
            }),
            contentType: "application/json",
            dataType: "json"
        }).done(function (data) {
            $.cookie('access_token',data.access_token)
        }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
            alert("error");
        })
    });
});
