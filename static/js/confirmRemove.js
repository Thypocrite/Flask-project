function confirmRemove(button) {
    var confirmRemove = confirm("請問是否要將此商品移出購物車?");
    if (confirmRemove) {
        // Proceed with form submission
        button.closest('.remove-form').submit();
    }
}