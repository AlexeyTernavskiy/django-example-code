var password = $("#id_password1");
var confirm_password = $("#id_password2");

function validatePassword() {
    if (password.val() != confirm_password.val()) {
    } else {
        confirm_password.get(0).setCustomValidity('');
    }
}

password.on('change', validatePassword);
confirm_password.on('keyup', validatePassword);
