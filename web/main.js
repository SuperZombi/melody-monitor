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
    eel.get_media_info()
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
