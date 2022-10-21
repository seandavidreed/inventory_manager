function increment(id, mode) {
    var elem = document.getElementById(id);
    if (mode === 'i') {
        elem.value = parseInt(elem.value) + 1;
        return;
    }

    if (mode === 'd' && elem.value != 0) {
        elem.value = parseInt(elem.value) - 1;
    }
}