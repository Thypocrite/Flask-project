function confirmCheckOut(button) {
    var confirmCheckOut = confirm("請問是否要將結帳?");
    if (confirmCheckOut) {
        // Proceed with form submission
        button.closest('.checkout-form').submit();
    }
}