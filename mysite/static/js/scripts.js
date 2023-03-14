function toggle_row(row, button, increment, input) {
    var row = document.getElementById(row);
    var button = document.getElementById(button);
    var increment = document.getElementsByClassName(increment);
    var input = document.getElementById(input);
    if (button.value == "false") {
        row.style.backgroundColor = "#82D782";
        button.value = "true";
        increment[0].style.display = "none";
        increment[1].style.display = "none";
        input.style.color = "#000000";
        input.readOnly = true;
    }
    else {
        row.style.backgroundColor = "#FFFFFF";
        button.value = "false";
        increment[0].style.display = "block";
        increment[1].style.display = "block";
        input.style.color = "#CCCCCC";
        input.readOnly = false;
    }
    
}

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

function validateForm() {
    var form = document.forms["myForm"]["validate"];

    for (let i = 0; i < form.length; i++) {
        if (form[i].value == "false") {
            alert("Please confirm each inventory item.");
            return false;
        }
    }

    return true;
}