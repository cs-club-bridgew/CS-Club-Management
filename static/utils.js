function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}



function getStyle() {
    $("#navbar").load("/navbar/"); 
    tag = document.createElement("link")
    tag.rel = "stylesheet"

    themeID = getCookie("themeID")
    if(themeID == undefined)
        themeID = '1'
    tag.href = `/${themeID}.css`
    var head = document.getElementsByTagName("head")[0]

    if(!head.children[head.children.length - 1].tagName != "LINK")
        head.appendChild(tag)
}


