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

eel.expose(update_media_info);
function update_media_info(info) {
    console.log(info);

    if (info.title && info.status == "PLAYING"){
        document.querySelector(".track-info").classList.add("active")
        document.querySelector("#trackName").innerHTML = info.title
        document.querySelector("#trackAuthor").innerHTML = info.artist
        checkMarquee()

        if (info.thumbnail){
            document.querySelector("#trackImage").src = info.thumbnail
        }
        else{
            document.querySelector("#trackImage").src = "disk.svg"
        }
        if (info.total > 0){
            document.querySelector(".progress-bar").style.display = "block"
            document.querySelector(".progress-bar .progress").style.transition = ""
            let percent = info.current * 100 / info.total;
            document.querySelector(".progress-bar .progress").style.width = `${percent}%`
            if (info.status == "PLAYING"){
                let remain = info.total - info.current;
                setTimeout(_=>{
                    document.querySelector(".progress-bar .progress").style.transition = `${remain}s linear`
                    document.querySelector(".progress-bar .progress").style.width = "100%"
                }, 10)
            }
        } else{
            document.querySelector(".progress-bar").style.display = "none"
        }
    }
    else{
        document.querySelector(".track-info").classList.remove("active")
    }
}

async function load_settings(){
    let settings = await eel.get_user_settings()();
    Object.entries(settings).forEach(([key, value]) => {
        document.body.setAttribute(key, value)
    })
}

async function load_mods(){
    let files = await eel.get_mods_list()();
    files.forEach(file=>{
        if (file.endsWith(".css")){
            let e = document.createElement("link")
            e.rel = "stylesheet"
            e.href = `mods/${file}`
            document.head.appendChild(e)
        }
    })
}

eel.expose(update_url);
function update_url(url) {
    window.location.href = url;
}
