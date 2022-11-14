var ctl = true

window.onblur = () => {
    if (ctl) {
        window.alert('您跳出了本視窗\n已取消本次交易')
        ctl = false
        window.location.href = "/"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    let sec = parseInt(document.getElementById('clock').innerText)
    clock = setInterval(() => {
        sec--
        if (sec >= 0) {
            document.getElementById('clock').innerText = ` ${sec} `
        }
        else {
            window.alert('交易逾時\n已取消本次交易')
            clearInterval(clock)
            ctl = false
            window.location.href = "/"
        }
    }, "1000")
});

function Check() {
    ctl = false
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
        setTimeout(() => {
            ctl = true
        }, '50');
        return false
    }
};