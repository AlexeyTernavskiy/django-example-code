$(document).ready(function () {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
    }

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $('#like').on('click', function (event) {
        event.preventDefault();
        var likeMsg = $('.alert > span');
        var likeMsgAlert = function (message, alertType) {
            return $('main > article').before('' +
                '<div class="alert alert-' + alertType + ' alert-dismissible fade in" role="alert">' +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span>' +
                '</button>' +
                '<span>' + message + '</span>' +
                '</div>' +
                '');
        };
        return $.ajax({
            url: 'like/',
            type: 'POST',
            success: function (data) {
                if (likeMsg.length > 0) {
                    likeMsg.text(data.message);
                } else {
                    likeMsgAlert(data.message, 'info')
                }
                $('#like').find('samp').html(data.like_count);
            },
            error: function (data) {
                var message = $.parseJSON(data.responseText).message;
                if (likeMsg.length > 0) {
                    likeMsg.text(message);
                } else {
                    likeMsgAlert(message, 'danger');
                }
            },
        })
    });

});