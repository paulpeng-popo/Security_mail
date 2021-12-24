const startbutton = document.getElementById("GetStart");

startbutton.addEventListener('click', () => {
    window.location.href = "https://nsysunmail.ml/authorize"
}, false)

let menulist = document.getElementById("MenuList");

function togglemenu() {
    if (menulist.style.maxHeight == "0px") {
        menulist.style.maxHeight = "260px";
    } else {
        menulist.style.maxHeight = "0px";
    }
}

const icon = document.querySelector('.toggleMenu');
const show = document.querySelector('.mobileNav');

icon.addEventListener('click', () => {
    icon.classList.toggle('open');
    show.classList.toggle('active');
});
