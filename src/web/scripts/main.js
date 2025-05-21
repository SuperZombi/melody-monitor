function checkMarquee(){
    let trackName = document.getElementById('trackName');
    let trackDetails = document.querySelector('.track-details');
    if (trackName.offsetWidth > trackDetails.offsetWidth) {
        trackName.classList.add('marquee');
    } else {
        trackName.classList.remove('marquee');
    }
}
window.onload=_=>{
    load_settings()
    load_mods()
    setTimeout(_=>{
        eel.get_media_info()
    }, 1000)
}
var timeRenderer;

eel.expose(update_media_info);
function update_media_info(info) {
    console.log(info);

    if (info.title && info.status == "PLAYING"){
        document.querySelector(".track-info").classList.add("active")
        document.querySelector("#trackName").innerHTML = info.title
        document.querySelector("#trackAuthor").innerHTML = info.artist
        if (timeRenderer){clearTimeout(timeRenderer)}
        checkMarquee()

        if (info.thumbnail){
            document.querySelector("#trackImage").src = info.thumbnail
        }
        else{
            document.querySelector("#trackImage").src = document.querySelector("#trackImage").getAttribute("default")
        }
        if (info.total > 0){
            document.querySelector(".progress-bar").classList.remove("hide")
            document.querySelector(".time").classList.remove("hide")
            document.querySelector(".progress-bar .progress").style.transition = ""
            let percent = info.current * 100 / info.total;
            document.querySelector(".progress-bar .progress").style.width = `${percent}%`

            document.querySelector(".time-current").innerHTML = formatTime(info.current)
            document.querySelector(".time-total").innerHTML = formatTime(info.total)

            let remain = info.total - info.current;
            setTimeout(_=>{
                document.querySelector(".progress-bar .progress").style.transition = `${remain}s linear`
                document.querySelector(".progress-bar .progress").style.width = "100%"
            }, 10)

            let targetTime = getUnixTime() + remain
            function renderTime(){
                let timeRemaining = Math.max(0, targetTime - getUnixTime())
                let currentTime = info.total - timeRemaining
                document.querySelector(".time-current").innerHTML = formatTime(currentTime)
                if (timeRemaining <= 0){return}
                timeRenderer = setTimeout(renderTime, 1000)
            }
            timeRenderer = setTimeout(renderTime, 1000)
        } else{
            document.querySelector(".progress-bar").classList.add("hide")
            document.querySelector(".time").classList.add("hide")
        }
    }
    else{
        document.querySelector(".track-info").classList.remove("active")
    }
}

async function load_settings(){
    let settings = await eel.get_user_settings()();
    Object.entries(settings.attrs).forEach(([key, value]) => {
        document.body.setAttribute(key, value)
    })
    Object.entries(settings.vars).forEach(([key, value]) => {
        document.body.style.setProperty(`--${key}`, value);
    })
}

async function load_mods(){
    let files = await eel.get_mods_files()();
    files.forEach(file=>{
        if (file.endsWith(".css")){
            let e = document.createElement("link")
            e.rel = "stylesheet"
            e.href = `mods/${file}`
            document.head.appendChild(e)
        }
    })
    let mods_settings = await eel.get_mods_settings()();
    Object.entries(mods_settings.attrs).forEach(([key, value]) => {
        document.body.setAttribute(key, value)
    })
    Object.entries(mods_settings.vars).forEach(([key, value]) => {
        document.body.style.setProperty(`--${key}`, value);
    })
}

eel.expose(update_url);
function update_url(url) {
    window.location.href = url;
}
function getUnixTime(){
    return Math.floor(Date.now() / 1000)
}
function formatTime(seconds) {
    let h = Math.floor(seconds / 3600);
    let m = Math.floor((seconds % 3600) / 60);
    let s = seconds % 60;

    let mm = String(m).padStart(2, '0');
    let ss = String(s).padStart(2, '0');

    if (h > 0) {
        let hh = String(h).padStart(2, '0');
        return `${hh}:${mm}:${ss}`;
    } else {
        return `${mm}:${ss}`;
    }
}
