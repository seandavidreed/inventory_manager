function increment(id, mode) {
    var elem = document.getElementById(id);
    elem.style.color = "#000000";
    if (mode === 'i') {
        elem.value = parseInt(elem.value) + 1;
        return;
    }

    if (mode === 'd' && elem.value != 0) {
        elem.value = parseInt(elem.value) - 1;
    }
}

// Change the color of any order entries that are zero
function check_qty(id) {
    var elem = document.getElementById(id);
    if (elem.innerHTML === '0') {
        elem.style.color = "#CCCCCC";
    }
}

function toggle_display(page) {
    var elements = document.getElementsByClassName("toggle");
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].innerHTML != page) {
            elements[i].style.display = "block";
        }
    }
}