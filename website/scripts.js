var API_BASE_URL = "https://q7dnar5wh8.execute-api.us-east-1.amazonaws.com/prod";

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("sayButton").onclick = function () {
        var text = document.getElementById('postText').value.trim();
        var voice = document.getElementById('voiceSelected').value;
        
        if (!text) {
            alert("Please enter some text to convert to speech.");
            return;
        }
        
        var inputData = {
            "voice": voice,
            "text": text
        };

        fetch(API_BASE_URL + "/new_post", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputData)
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("postIDreturned").textContent = "Post ID: " + data;
            document.getElementById('postId').value = data;
        })
        .catch(error => {
            alert("Error: " + error);
        });
    };

    document.getElementById("searchButton").onclick = function () {
        var postId = document.getElementById('postId').value.trim();

        if (postId === "") {
            alert("Please enter a post ID.");
            return;
        }

        fetch(API_BASE_URL + "/get-post?postId=" + postId)
        .then(response => response.json())
        .then(data => {
            var tbody = document.querySelector('#posts tbody');
            tbody.innerHTML = '';

            data.forEach(function(item) {
                var row = tbody.insertRow();
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.voice}</td>
                    <td>${item.text}</td>
                    <td>${item.status}</td>
                    <td>
                        ${item.url ? `<audio controls><source src="${item.url}" type="audio/mpeg"></audio><br><a href="${item.url}" download>⬇️ Download</a>` : 'Processing...'}
                        <br><button onclick="refreshPost('${item.id}')" style="background:#4CAF50;color:white;border:none;padding:5px;border-radius:3px;cursor:pointer;">🔄 Refresh</button>
                    </td>
                `;
            });
        })
        .catch(error => {
            alert("Error: " + error);
        });
    };

    document.getElementById("postText").onkeyup = function () {
        var length = document.getElementById('postText').value.length;
        document.getElementById("charCounter").textContent = "Characters: " + length;
    };
});

function refreshPost(postId) {
    fetch(API_BASE_URL + "/get-post?postId=" + postId)
    .then(response => response.json())
    .then(data => {
        var tbody = document.querySelector('#posts tbody');
        tbody.innerHTML = '';
        
        data.forEach(function(item) {
            var row = tbody.insertRow();
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.voice}</td>
                <td>${item.text}</td>
                <td>${item.status}</td>
                <td>
                    ${item.url ? `<audio controls><source src="${item.url}" type="audio/mpeg"></audio><br><a href="${item.url}" download>⬇️ Download</a>` : 'Processing...'}
                    <br><button onclick="refreshPost('${item.id}')" style="background:#4CAF50;color:white;border:none;padding:5px;border-radius:3px;cursor:pointer;">🔄 Refresh</button>
                </td>
            `;
        });
    })
    .catch(error => {
        alert("Error refreshing: " + error);
    });
}