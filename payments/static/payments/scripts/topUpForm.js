$(document).ready(function() {

    //zip code formatting
    $("#postal-code").keyup(function() {
        zipcode = $(this).val();
        zipcode = zipcode.replace(/-/g, '');      // remove all occurrences of '-'

        if(zipcode.length >= 5 ) {
            $(this).val(zipcode.substring(0, 2) + "-" + zipcode.substring(2, 5));
        }
    });

    let initialAddress = $("#form-initial");
    let oldAddress = $('#div_id_address_action');
    let newAddress = $('#new-address');

    let newOrOldAddress = $("input[type=radio][name=address_choice]");

    if (initialAddress.length > 0) {
        newOrOldAddress.prop('required',true);
        newAddress.hide();
        oldAddress.show();

        newOrOldAddress.change(function() {
            if (this.value == "new") {
                newAddress.slideDown();
                initialAddress.slideUp();
            } else if (this.value == "last") {
                newAddress.slideUp();
                initialAddress.slideDown();
            }
        });
    } else {
        oldAddress.hide();
        newAddress.show();
    }
});