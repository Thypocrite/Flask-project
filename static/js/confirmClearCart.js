function confirmClearCart(button) {
    var confirmClearCart = confirm("請問是否要將購物車清空?");
    if (confirmClearCart) {
        // Proceed with form submission
        button.closest('.clear-form').submit();
    }
}