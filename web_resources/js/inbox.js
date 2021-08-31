const send_btn = document.getElementById("send_button")
let t = document.getElementById("token")
let rt = document.getElementById("refresh_token")

send_btn.addEventListener("click", (event) => {
    allcookies = document.cookie.split(";");
    for (let i = 0; i < allcookies.length; i++) {
        thisCookie = allcookies[i].split("=");
        cName = unescape(thisCookie[0]);
        cValue = unescape(thisCookie[1]);
        if (cName.indexOf("gmailapi_token") != -1) { t.value = cValue; }
        if (cName.indexOf("gmailapi_refresh_token") != -1) { rt.value = cValue; }
    }
});

function getMessageShow(msg_id, token) {
    window.location.href = 'https://nsysunmail.ml/show?id=' + msg_id + '&query=' + token;
}

// function getSelectedCheckbox(name) {
// 	const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
// 	let values = [];
// 	checkboxes.forEach((checkbox) => {
// 		values.push(checkbox.value);
// 	});
// 	return values;
// }

// const decrypt = document.querySelector('#decrypt_button');
// decrypt.addEventListener('click', (event) => {
// 	ids = getSelectedCheckbox('a_mail');
//     alert(ids)
// });
