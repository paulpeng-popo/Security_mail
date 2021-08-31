let signoutButton = document.getElementById('SignOutButton');
let sendButton = document.getElementById('SendMailButton');
let decrypt = document.getElementById('DecryptButton');
let CLIENT_ID = '852787793793-6a445i2ptcdo7n0ia17islr0vsfhh2r4.apps.googleusercontent.com';
let API_KEY = 'fFZwcvBy5mwCpSLG6T-2mvtk';
let SCOPES = 'https://mail.google.com/';

function handleSendClick(event) {
    window.location.href = "send.html";
}

function handleSignoutClick(event) {
    window.location.href = "https://nsysunmail.ml/logout";
}

function handleClientLoad() {
    gapi.load('client:auth2', function () {
        gapi.auth2.init().then(() => {
            signoutButton.onclick = handleSignoutClick;
            sendButton.onclick = handleSendClick;
        })
    });
    gapi.client.setApiKey(API_KEY);
    window.setTimeout(checkAuth, 1);
}

function checkAuth() {
    gapi.auth.authorize({
        client_id: CLIENT_ID,
        scope: SCOPES,
        immediate: true
    }, handleAuthResult);
}

function handleAuthResult(authResult) {
    if (authResult && !authResult.error) {
        loadGmailApi();
    }
}

function loadGmailApi() {
    gapi.client.load('gmail', 'v1', displayInbox);
}

function displayInbox() {
    let request = gapi.client.gmail.users.messages.list({
        'userId': 'me',
        'labelIds': 'INBOX',
        'maxResults': 30
    });

    if ($('.message-list')[0].innerText != "") {
        $('.message-list').empty();
    }

    request.execute(function (response) {
        $.each(response.messages, function () {
            let messageRequest = gapi.client.gmail.users.messages.get({
                'userId': 'me',
                'id': this.id
            });
            messageRequest.execute(appendMessageRow);
        });
    });

    setTimeout(() => {
        if ($('.message-list')[0].innerText == "") {
            $('.message-list').append('<h3>What a clean inbox you have...</h3>');
        }
    }, 5000)
}

function appendMessageRow(message) {

    $('#mail-list .box-gap .message-list').append(
        '<li id="message-link-' + message.id + '" class="mail encrypt">\
                    <div class="index"></div>\
                    <div class="group">\
                        <div style="color: brown; font-weight: 1000;">&emsp;Date:</div>\
                        <div>' + getHeader(message.payload.headers, 'Date') + '</div>\
                    </div>\
                    <div class="group">\
                        <div style="color: brown; font-weight: 1000;">&emsp;From:</div>\
                        <div>' + getHeader(message.payload.headers, 'From') + '</div>\
                    </div>\
                    <div class="group">\
                        <div style="color: brown; font-weight: 1000;">Subject:</div>\
                        <div style="font-weight: bold;">' + getHeader(message.payload.headers, 'Subject') + '</div>\
                    </div>\
                </li>'
    );

    $('body').append(
        '<div class="modal fade" id="message-modal-' + message.id + '" tabindex="-1">\
                    <div class="modal-dialog">\
                        <div class="modal-content">\
                            <div class="modal-header">\
                                <button id="close-message-' + message.id + '" class="close">&times;</button>\
                                <h4 class="modal-title">' + getHeader(message.payload.headers, 'Subject') + '</h4>\
                            </div>\
                            <div class="modal-body">\
                                <iframe id="message-iframe-' + message.id + '" srcdoc="<p>Loading...</p>">\
                                </iframe>\
                            </div>\
                        </div>\
                    </div>\
                </div>'
    )

    let modal = document.getElementById('message-modal-' + message.id);
    $('#message-link-' + message.id).on("click", () => {
        modal.style.display = "block"
        let ifrm = $('#message-iframe-' + message.id)[0].contentWindow.document;
        console.log(getBody(message.payload));
        $('body', ifrm).html(getBody(message.payload));
    });
    $('#close-message-' + message.id).on("click", () => {
        modal.style.display = "none"
    });

}

function getHeader(headers, index) {
    let header = '';

    $.each(headers, function () {
        if (this.name === index) {
            header = this.value;
        }
    });
    return header;
}

function getBody(message) {
    let encodedBody = '';
    if (typeof message.parts === 'undefined') {
        encodedBody = message.body.data;
    } else {
        encodedBody = getHTMLPart(message.parts);
    }
    encodedBody = encodedBody.replace(/-/g, '+').replace(/_/g, '/').replace(/\s/g, '');
    return decodeURIComponent(escape(window.atob(encodedBody)));
}

function getHTMLPart(arr) {
    for (let x = 0; x <= arr.length; x++) {
        if (typeof arr[x].parts === 'undefined') {
            if (arr[x].mimeType === 'text/html') {
                return arr[x].body.data;
            }
        } else {
            return getHTMLPart(arr[x].parts);
        }
    }
    return '';
}

setTimeout(() => {
    alert("Idle for a long time. Please login again.");
    gapi.auth2.getAuthInstance().signOut();
    location.reload();
    window.location.href = "https://nsysunmail.ml/";
}, 600000);
