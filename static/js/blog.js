
"use strict";

/*=====================================
window.addEventListener
======================================= */

window.addEventListener('DOMContentLoaded', function()
{
    const navi = document.querySelector('.navi-blog');

    if (navi != null)
    {
        const title = document.querySelector('.title');
        const pathname = location.pathname.split('/');
        title.innerText=pathname[2];
        navi.innerText=pathname[2];
    }

});

/*=====================================
reply dynamic input box
======================================= */

function newReplyBox(replyNum,depth)
{
    const replyNode = document.querySelector(".reply-input");
    const targetNode = document.querySelector(".reply-"+ replyNum);
    const newNode = replyNode.cloneNode(true);
    const author = document.getElementById("name");

    targetNode.appendChild(newNode);
    replyNode.parentNode.removeChild(replyNode);

    document.querySelector("#reply-create-fbt").style.display = 'block';
    document.querySelector("#reply-update-fbt").style.display = 'none';

    const depth_input = document.getElementById("depth");
    const parent_input = document.getElementById("parent");

    if (depth < 3) {
        depth_input.setAttribute("value",depth+1);
    }
    else {
        depth_input.setAttribute("value",3);
    }

    parent_input.setAttribute("value",replyNum);

    if ( 1 < depth) {
        reply_input_box = document.getElementById("comment");
        reply_input_box.textContent= "@"+author.textContent + " ";

    }
    else {
        reply_input_box = document.getElementById("comment");
        reply_input_box.textContent= "";
    }
}