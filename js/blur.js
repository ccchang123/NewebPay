var ctl = true

window.onblur = function() {
    if (ctl) {
        window.alert('您跳出了本視窗\n已取消本次交易')
        ctl = false
        window.location.href = "/"
    }
};

document.addEventListener('DOMContentLoaded', (event) => {
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