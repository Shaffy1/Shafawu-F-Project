var API_BASE_URL = "https://q7dnar5wh8.execute-api.us-east-1.amazonaws.com/prod";

$(document).ready(function() {
    $("#sayButton").click(function () {
        var text = $('#postText').val().trim();
        var voice = $('#voiceSelected').val();
        
        if (!text) {
            alert("Please enter some text to convert to speech.");
            return;
        }
        
        var inputData = {
            "voice": voice,
            "text": text
        };

        $.ajax({
            url: API_BASE_URL + "/new_post",
            type: 'POST',
            data: JSON.stringify(inputData),
            contentType: 'application/json; charset=utf-8',
            success: function (response) {
                $("#postIDreturned").text("Post ID: " + response);
                $('#postId').val(response);
            },
            error: function (xhr) {
                alert("Error: " + xhr.responseText);
            }
        });
    });

    $("#searchButton").click(function () {
        var postId = $('#postId').val().trim();

        if (postId === "") {
            alert("Please enter a post ID.");
            return;
        }

        $.ajax({
            url: API_BASE_URL + "/get-post?postId=" + postId,
            type: 'GET',
            success: function (response) {
                $('#posts tbody').empty();

                if (typeof response === "string") {
                    response = JSON.parse(response);
                }

                $.each(response, function (i, data) {
                    var player = "";
                    var download = "";
                    
                    if (data['url']) {
                        player = "<audio controls><source src='" + data['url'] + "' type='audio/mpeg'></audio>";
                        download = "<br><a href='" + data['url'] + "' download>⬇️ Download</a>";
                    } else {
                        player = "Processing...";
                    }

                    $("#posts tbody").append(
                        "<tr>" +
                        "<td>" + data['id'] + "</td>" +
                        "<td>" + data['voice'] + "</td>" +
                        "<td>" + data['text'] + "</td>" +
                        "<td>" + data['status'] + "</td>" +
                        "<td>" + player + download + "<br><button onclick='refreshPost(\"" + data['id'] + "\")' style='background:#4CAF50;color:white;border:none;padding:5px;border-radius:3px;cursor:pointer;'>🔄 Refresh</button></td>" +
                        "</tr>"
                    );
                });
            },
            error: function (xhr) {
                alert("Error: " + xhr.responseText);
            }
        });
    });

    $("#postText").keyup(function () {
        var length = $(this).val().length;
        $("#charCounter").text("Characters: " + length);
    });
});

function refreshPost(postId) {
    $.ajax({
        url: API_BASE_URL + "/get-post?postId=" + postId,
        type: 'GET',
        success: function (response) {
            $('#posts tbody').empty();
            
            if (typeof response === "string") {
                response = JSON.parse(response);
            }
            
            $.each(response, function (i, data) {
                var player = "";
                var download = "";
                
                if (data['url']) {
                    player = "<audio controls><source src='" + data['url'] + "' type='audio/mpeg'></audio>";
                    download = "<br><a href='" + data['url'] + "' download>⬇️ Download</a>";
                } else {
                    player = "Processing...";
                }

                $("#posts tbody").append(
                    "<tr>" +
                    "<td>" + data['id'] + "</td>" +
                    "<td>" + data['voice'] + "</td>" +
                    "<td>" + data['text'] + "</td>" +
                    "<td>" + data['status'] + "</td>" +
                    "<td>" + player + download + "<br><button onclick='refreshPost(\"" + data['id'] + "\")' style='background:#4CAF50;color:white;border:none;padding:5px;border-radius:3px;cursor:pointer;'>🔄 Refresh</button></td>" +
                    "</tr>"
                );
            });
        },
        error: function (xhr) {
            alert("Error refreshing: " + xhr.responseText);
        }
    });
}