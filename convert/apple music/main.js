
songs = document.getElementsByClassName("songs-list-row__song-name");
artists = document.getElementsByClassName("songs-list__song-link-wrapper");
thelist = "";
for(let i = 0; i < songs.length; i++){
    let song = ""
    for(let j = 0; j < songs[i].innerText.length; j++){
        console.log(songs[i].innerText.charAt(j))
        if (songs[i].innerText.charAt(j) == "[" || songs[i].innerText.charAt(j) == "(")
            break;
        song+=songs[i].innerText.charAt(j)
    }
    thelist += "\""+artists[i].innerText+" - "+song+"\",\n";
}
console.log(thelist);