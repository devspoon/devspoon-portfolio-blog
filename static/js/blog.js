
"use strict";

/*=====================================
window.addEventListener
======================================= */

window.addEventListener('DOMContentLoaded', function()
{
    const navi = document.querySelector('.navi-blog');
    const list_write = document.querySelector('#blog-list-write');
    const list_detail = document.querySelectorAll('#blog-detail-link');
    if (navi != null) // This web page is a blog.
    {
        const pageTitle = document.querySelector('.title'); //class
        const title = document.querySelector('title'); //tag
        const pathName = location.pathname.split('/');
        pageTitle.innerText=pathName[2];
        navi.innerText=pathName[2];
        title.innerText=pathName[2];
    }

    // if (list_write != null) // This web page is a blog list.
    // {
    //     let post_num = window.location.href+"create/"
    //     list_write.setAttribute('href',post_num);
    // }

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

/*=====================================
board move a new page
======================================= */

function boardWrite()
{
    const full_url = location.href + 'write';

    location.href=full_url;
}