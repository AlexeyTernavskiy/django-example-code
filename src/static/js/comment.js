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

    var commentForm = $('#comment-form');
    var commentText = $('#comment-text');
    var commentSubmit = $('#comment-submit');
    var noComments = $('#no-comments');

    commentText.on('keyup', function () {
        if ($(this).val() !== '') {
            return commentSubmit.prop('disabled', false);
        } else {
            return commentSubmit.prop('disabled', true);
        }
    });

    commentSubmit.on('click', function (e) {
        e.preventDefault();
        if (commentText.val() !== '') {
            var commentMsgAlert = function (message, alertType) {
                return commentForm.before('' +
                    '<div class="alert alert-' + alertType + ' alert-dismissible fade in" role="alert">' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                    '</button>' +
                    '<span>' + message + '</span>' +
                    '</div>' +
                    '');
            };
            return $.ajax({
                type: 'POST',
                url: 'comment/',
                data: {
                    'comment': commentText.val()
                },
                success: function (data) {
                    var commentMsg = $('#comment-msg');

                    if (commentMsg.length > 1) {
                        commentMsg.detach();
                        commentForm.removeClass('has-danger');
                    }

                    commentMsg = $('.alert > span');
                    commentText.val('');
                    commentSubmit.prop('disabled', true);

                    commentForm.after(data.html);

                    if (commentMsg.length > 0) {
                        commentMsg.text(data.message);
                    } else {
                        commentMsgAlert(data.message, 'info');
                    }
                },
                error: function (data) {
                    var commentMsg = $('#comment-msg');
                    var error = $.parseJSON(data.responseText);
                    commentForm.addClass('has-danger');
                    if (commentMsg.length > 0) {
                        commentMsg.text(error.message);
                    } else {
                        commentText.before('' +
                            '<div id="comment-msg" class="alert alert-danger" role="alert">' +
                            '' + error.message + '' +
                            '</div>');
                    }
                },
                complete: function () {
                    if (noComments.length > 0) {
                        noComments.detach();
                    }
                }
            });
        }
    });

    $('#last-comments').on('click', function (e) {
        var comments = $('[data-id]');
        var lastCommentId = $(comments[comments.length - 1]).data('id') || 0;
        var noComments = $('#no-comments');
        e.preventDefault();

        return $.ajax({
            type: 'POST',
            url: 'comments/last/',
            data: {
                'id': lastCommentId
            },
            success: function (data) {
                if (data.html) {
                    if (noComments.length > 0) {
                        noComments.after(data.html);
                        noComments.detach();
                    }
                    else {
                        $(comments[comments.length - 1]).after(data.html);
                    }

                }
                if (data.disabled) {
                    $('#last-comments').prop('disabled', true);
                }
            },
            error: function () {
                return false
            }
        })
    });
});
