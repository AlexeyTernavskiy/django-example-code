$(document).ready(function () {

    $('#filter_form').on('change', function (event) {
        var selected;
        selected = document.getElementById('id_filter').value;
        if (!selected) {
            return false;
        } else {
            return event.target.form.submit();
        }
    });
});