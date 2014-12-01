// init vars
var modal = $("#server-modal");
var alert = $("#server-alert");

// hide
alert.hide();

$(".server").click(function(e) {
    e.preventDefault();

    // get values from item
    var address = $(this).attr("data-address");
    var port = $(this).attr("data-port");

    // do ajax
    $.ajax({
        url: "/server?address=" + address + "&port=" + port,
        type: "GET",
        dataType: "json",
        context: this,
        success: function(result) {
            // set vars for modal
            var header = modal.find(".modal-header");
            var body = modal.find(".modal-body");
            var joinBtn = modal.find("button#join");

            modal.find(".modal-body").html("Server name: " + result.name);
            if (result.status)
                modal.find("button#join").prop("disabled", false);
            else
                modal.find("button#join").prop("disabled", true);
            modal.modal('show');
            console.log(result);
        },
        error: function() {
            alert.show().delay(3000).fadeOut(300);
        },
        timeout: 3000
    });
});
