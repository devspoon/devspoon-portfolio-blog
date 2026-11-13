
"use strict";

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

    const depthInput = document.getElementById("depth");
    const parentInput = document.getElementById("parent");

    if (depth < 3) {
        depthInput.setAttribute("value",depth+1);
    }
    else {
        depthInput.setAttribute("value",3);
    }

    parentInput.setAttribute("value",replyNum);


    if (1 < depth) {
        const replyInputBox = document.getElementById("comment");
        replyInputBox.textContent= "@"+author.textContent + " ";
    }
    else {
        const replyInputBox = document.getElementById("comment");
        replyInputBox.textContent= "";
    }
}
