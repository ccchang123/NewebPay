document.addEventListener("DOMContentLoaded", () => {
    console.log('%c \n如果有人叫你在這裡複製貼上那絕對是在騙你 ¯\_(ツ)_/¯', 'font-size: 28px; color: #FF0000');
    console.log('%c \n如果你知道你在幹嘛, 歡迎加入我們 \\(.D˙)/', 'font-size: 23px');
    console.log('%c \nCopyright © 2022 CHANG, YU-HSI. All rights reserved.', 'color: rgba(237, 237, 237, 0.5)');
});

document.oncopy = () => {
    return false
};

document.onpaste = () => {
    return false
};

document.oncut = () => {
    return false
};

document.oncontextmenu = () => {
    return false
};

document.onkeyup = () => {
    if (event.key == 'PrintScreen') {
        setTimeout(() => {
            alert('提醒您\n請務必妥善保管擷取之螢幕畫面，以保障您的權益')
        }, '200');
    }
};

function input_num() {
    if (event.target.value != 0) {
        document.getElementById('num').innerText = `${parseInt(event.target.value) + 30} `
    }
};