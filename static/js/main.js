$("[data-toggle='modal']").click(function(e) {
    e.preventDefault();

    // get values from data-* for ajax request
    var address = $(this).attr('data-address');
    var port = $(this).attr('data-port');

    // modal globals
    var modal = $("#server-modal");

    // do ajax request
    $.ajax({
        url: "/server?address=" + address + "&port=" + port,
        type: "GET",
        dataType: "json",
        context: this,
        success: function(values) {
            modal.find(".modal-body").html("Information about: " + values.name);
            if (values.status == false)
                modal.find("button#join").prop("disabled", true);
            else
                modal.find("button#join").prop("disabled", false);
            console.log(values);
        },
        error: function() {
            alert("Problem fetching JSON");
        }
    })
});