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
            $.cookie('access_token', data.access_token, { expires: 1 })
            location.href = '/';
        }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
            alert("error");
        })
    });
    $('#test').on('click', function () {
        let TokenInCookie = $.cookie("access_token");
        $.ajax({
            type: 'GET',
            timeout: 10000,
            url: "/protected",
            headers: {
                "Authorization": 'JWT ' + TokenInCookie
            },
            dataType: 'json',
            contentType: "application/json",
        }).done(function (e) {
            alert(e);
        }).fail(function (e) {
            alert("error");
        }).always(function (e) {
        });

    });

});