document.addEventListener("DOMContentLoaded", function() {
    console.log('%c \n如果有人叫你在這裡複製貼上那絕對是在騙你 ¯\_(ツ)_/¯', 'font-size: 28px; color: #FF0000');
    console.log('%c \n如果你知道你在幹嘛, 歡迎加入我們 \\(.D˙)/', 'font-size: 23px');
    console.log('%c \nCopyright © 2022 CHANG, YU-HSI. All rights reserved.', 'color: rgba(237, 237, 237, 0.5)');
});

function Check() {
    const id = document.getElementsByName('minecraft_id')[0].value
    const email = document.getElementsByName('email')[0].value
    const amount = document.getElementsByName('amount')[0].value
    const msg = document.getElementsByName('msg')[0].placeholder
    let check = window.confirm(`請確認以下內容是否正確:\n遊戲ID: ${id}\n電子信箱: ${email}\n贊助金額(含手續費30元): ${amount}\n留言: ${msg}`);
    if (check) {
        window.alert('若後續訂單內容有誤，請自行負責')
        return true
    }
    else {
        return false
    }
};