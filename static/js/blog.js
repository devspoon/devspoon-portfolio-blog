
"use strict";

/*=====================================
window.addEventListener
======================================= */

window.addEventListener('DOMContentLoaded', function()
{
    const navi = document.querySelector('.navi-blog');
    const detail_button_group = document.querySelector('#detail-button-group');
    const detail_nav_group = document.querySelector('#navigation-group');
    const list_th_title = document.querySelectorAll('#th-title');

    if (navi != null)
    {
        const pageTitle = document.querySelector('.title'); //class
        const title = document.querySelector('title'); //tag
        const pathName = location.pathname.split('/');
        pageTitle.innerText=pathName[2];
        navi.innerText=pathName[2];
        title.innerText=pathName[2];
    }

    if (detail_button_group != null)
    {
        const update_ = document.querySelector('#update-button');
        const delete_ = document.querySelector('#delete-button');
        const pk = update_.getAttribute('href');
        let url = location.pathname.split('/');
        const update_url = location.origin+'/'+url[1]+'/'+url[2]+'/update/'+pk+'/'
        const delete_url = location.origin+'/'+url[1]+'/'+url[2]+'/delete/'+pk+'/'
        update_.setAttribute('href',update_url);
        delete_.setAttribute('href',delete_url);
    }

    if (detail_nav_group != null)
    {
        const left = document.querySelector('#nav-left');
        const right = document.querySelector('#nav-right');
        let url = location.pathname.split('/');

        if (left != null)
        {
            const pk = left.getAttribute('href');
            const left_url = location.origin+'/'+url[1]+'/'+url[2]+'/detail/'+(parseInt(pk)-1)+'/'
            left.setAttribute('href',left_url);
        }

        if (right != null)
        {
            const pk = right.getAttribute('href');
            const right_url = location.origin+'/'+url[1]+'/'+url[2]+'/detail/'+(parseInt(pk)+1)+'/'
            right.setAttribute('href',right_url);
        }

    }
    if (list_th_title != null)
    {
        let pk;
        let url;
        for (let i=0; i < list_th_title.length; i++)
        {
            pk = list_th_title[i].getAttribute('href');
            url = location.pathname.split('/');
            url = location.href + 'detail/'+pk+'/';
            list_th_title[i].setAttribute('href',url);
        }
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

function boardCreate()
{
    const full_url = location.href + 'create';

    location.href=full_url;
}