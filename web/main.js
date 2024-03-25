function checkMarquee(){
    let trackName = document.getElementById('trackName');
    let trackDetails = document.querySelector('.track-details');
    if (trackName.offsetWidth > trackDetails.offsetWidth) {
        trackName.classList.add('marquee');
    }
}
window.onload=_=>{}

eel.expose(update_media_info);
function update_media_info(info) {
    document.querySelector("#trackName").classList.remove('marquee');
    console.log(info);

    if (info.title){
        document.querySelector("#trackName").innerHTML = info.title
        document.querySelector("#trackAuthor").innerHTML = info.artist
        checkMarquee()

        if (info.thumbnail){
            document.querySelector("#trackImage").src = info.thumbnail
        }
        else{
            document.querySelector("#trackImage").src = "disk.svg"
        } 
    }
    else{
        document.querySelector("#trackName").innerHTML = ""
        document.querySelector("#trackAuthor").innerHTML = ""
        document.querySelector("#trackImage").src = "disk.svg"
    }
}
