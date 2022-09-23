
/*=====================================
global variable and function
======================================= */

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

let create_state = true;
let update_state = true;
let delete_state = true;


function range(start,end) {
    let array = [];

    for (let i = start; i < end; ++i) {
      array.push(i);
    }

    return array;
}

/*=====================================
blog like event
======================================= */

const likeToggler = document.querySelector(".lni-heart");

likeToggler.addEventListener('click', async function() {
    const likeTogglerDiv = document.querySelector(".like-btn");
    const likeCount = document.querySelector(".like_count");

    const url = window.location.origin + '/opensource/like/json/';
    let post_num = window.location.href.split('/');
    post_num = post_num[post_num.length - 2];
    const full_url = url + post_num + '/';

    try {
        let res = await axios.get(full_url);
        likeCount.textContent=res.data.like_count;
        likeToggler.classList.toggle('clicked');
        likeTogglerDiv.setAttribute('onfocus','this.blur()');
        likeTogglerDiv.setAttribute('readonly',true);
    } catch (err){
        console.log('like error : ' ,err);
    }
});


/*=====================================
Get a list of replies from a blog
======================================= */

function resetReplyInputBox()
{
    const replyNode = document.querySelector(".reply-input");
    const resetReplyNode = document.querySelector(".comment-content");
    const newNode = replyNode.cloneNode(true);
    resetReplyNode.insertAdjacentElement('beforeend',newNode);
    replyNode.parentNode.removeChild(replyNode);
}


function setReplyLocation(replies,reply_key,snippet){
    const reply_root = document.querySelector(".comment-content");

    if (replies[reply_key].depth == 0)
    {
        reply_root.insertAdjacentHTML('beforeend',snippet);
        resetReplyInputBox();
    }
    else if (replies[reply_key].depth == 1)
    {
        const parent_element = document.querySelector(".root-reply.root-"+replies[reply_key].parent);0
        const nodes = document.querySelector(".fist-reply.parent-"+replies[reply_key].parent);

        if (nodes)
            reply_root.insertAdjacentHTML('beforeend',snippet);
        else
            parent_element.insertAdjacentHTML('afterend',snippet);

        resetReplyInputBox();
    }
    else if (replies[reply_key].depth == 2)
    {
        const parent_element = document.querySelector(".fist-reply.node-"+replies[reply_key].parent);
        const nodes = document.querySelectorAll(".second-reply.parent-"+replies[reply_key].parent);

        if (nodes.length != 0)
        {
            if (nodes.length == 1)
            {
                nodes[0].insertAdjacentHTML('afterend',snippet);
            }
            else
            {
                nodes[nodes.length-1].insertAdjacentHTML('afterend',snippet);
            }
        }
        else
        {
            parent_element.insertAdjacentHTML('afterend',snippet);
        }
        resetReplyInputBox();
    }
    else // depth 3
    {
        let parent_element = document.querySelector(".depth-"+(Number(replies[reply_key].depth)-1)+'.node-'+replies[reply_key].parent);
        const sibling_nodes = document.querySelectorAll(".depth-"+replies[reply_key].depth+'.parent-'+replies[reply_key].parent);

        if (parent_element == null) //if it is a reply of '@comment' case
        {
            parent_element = document.querySelector(".depth-"+(Number(replies[reply_key].depth))+'.node-'+replies[reply_key].parent);
        }

        if (sibling_nodes.length != 0)
        {
            let last_sibling_node_classes = null;

            if (sibling_nodes.length == 1)
            {
                last_sibling_node_classes = sibling_nodes[0].classList; //get last sibling node's class names
            }
            else
            {
                last_sibling_node_classes = sibling_nodes[sibling_nodes.length-1].classList; //get last sibling node's class names
            }

            const last_sibling_node_pk = last_sibling_node_classes[3]; //get last sibling node's pk array of from class names
            const last_sibling_node = document.querySelector(".depth-"+replies[reply_key].depth+'.'+last_sibling_node_pk); //get last sibling node
            last_sibling_node.insertAdjacentHTML('afterend',snippet);
        }
        else
        {
            parent_element.insertAdjacentHTML('afterend',snippet);
        }

        resetReplyInputBox();
    }
}


function buildReplyStack(replies,url){

    //for (let reply in replies) {
    for (let reply = 1; reply < replies.length ; reply++)    {
        snippet = '';

        if (replies[reply].depth == 0)
        {
            snippet += '<div class="single-comment root-reply root-'+replies[reply].pk+'">\n';
        }
        else if (replies[reply].depth == 1)
        {
            snippet += '<div class="single-comment fist-reply parent-'+replies[reply].parent+' node-'+replies[reply].pk+'">\n';
        }
        else
        {
            snippet += '<div class="single-comment second-reply parent-'+replies[reply].parent+' node-'+replies[reply].pk+' depth-'+replies[reply].depth+'">\n';
        }

        // thembnail
        snippet += '<div class="author-info"> \n\
                       <div class="thumb"> \n\
                        <img src="'+ replies[reply].thumbnail +'" alt="Image"> \n\
                        </div>\n';

        // name
        snippet += '<div class="author-details reply-'+replies[reply].pk+'">\n\
                    <ul>\n\
                        <li class="name" id="name">'+replies[reply].author+'</li>\n\
                        <li class="meta-date ms-2" id="'+replies[reply].pk+'">'+replies[reply].created_at+'</li>\n\
                    </ul>\n';

        // comment
        snippet += '<p>'+replies[reply].comment+'</p>\n';

        //update, delete button
        snippet +=  '<div class="d-flex justify-content-end"> \n\
                        <a class="btn btn-outline-primary btn-sm mx-3 " href="javascript:void(0);" onclick="updateReplyBox('+replies[reply].pk+'); return false;">Update</a> \n\
                        <a class="btn btn-outline-secondary btn-sm mx-3" href="'+url+'delete/'+replies[reply].pk+'/">Delete</a> \n\
                    </div>\n';

        //reply button
        snippet +=  '<div class="d-flex justify-content-end mt-3"> \n\
                        <a class="btn btn-outline-danger btn-sm mx-3" href="javascript:void(0);"  onclick="newReplyBox('+replies[reply].pk+','+replies[reply].depth+'); return false;">Reply</a>\n\
                    </div>\n';

        // close brackets
        snippet += '        </div> \n\
                        </div> \n\
                    </div>\n';


        setReplyLocation(replies,reply,snippet);
    }
}



const replyList = async function(url,page=1) {
    try {
        const full_url = url+'reply/json/?page='+page;
        let res = await axios.get(full_url);
        buildReplyStack(res.data,full_url);
        buildPagination(res.data);
    }
    catch (err){
        console.log('reply list error : ' ,err);
    }

};


/*=====================================
Create a reply to a blog
======================================= */

function createReply()
{
    if (create_state == true)
    {
        create_state = false;
        document.querySelector('#reply-box-form').submit();
        return false;
    }
}


/*=====================================
Update a reply to a blog
======================================= */

async function updateReply(replyKey)
{
    if (update_state == true)
    {
        update_state=false;
        comment = document.getElementById("comment").value;

        if (comment)
        {
            try {
                const full_url = location.href+'reply/json/update/'+replyKey+'/';
                let res = await axios.post(full_url,{comment: comment,});
                update_state=true;
                document.querySelector(".reply-"+replyKey).querySelector("p").textContent = comment;
                document.getElementById("comment").value = "";
            }
            catch (err){
                console.log('reply list error : ' ,err);
            }
        }
        else
        {
            alert("Reply input can't be null!");
        }
    }
}


function updateReplyBox(replyNum)
{
    const replyNode = document.querySelector(".reply-input");
    const targetNode = document.querySelector(".reply-"+ replyNum);
    const newNode = replyNode.cloneNode(true);

    targetNode.appendChild(newNode);
    replyNode.parentNode.removeChild(replyNode);

    document.querySelector("#reply-create-fbt").style.display = 'none';
    update_bt=document.querySelector("#reply-update-fbt");
    update_bt.style.display = 'block';
    update_bt.setAttribute("onclick","updateReply("+replyNum+"); return false;");

    comment=targetNode.querySelector("p").innerText;

    reply_input_box = document.getElementById("comment");
    reply_input_box.textContent = comment;
}


/*=====================================
replies pagination
======================================= */

function paginationArrowButton(previous_state=1,next_state=1,pre_page=1,next_page=1)
{
    pagination_parent_node = document.querySelector('.pagination');
    let previous = '';
    let next = '';

    if (previous_state==true)
    {
        previous = '<li class="page-item" id="previous-li" >\n\
                        <a class="page-link" id="previous-link" href="javascript:void(0);" onclick="pageBox('+pre_page+'); return false;" aria-label="Previous">\n\
                            <span aria-hidden="true">&laquo;</span>\n\
                        </a>\n\
                    </li>';
    }
    else
    {
        previous = '<li class="page-item disabled" id="previous-li" >\n\
                        <a class="page-link" id="previous-link" href="#" tabindex="-1" aria-label="Previous">\n\
                            <span aria-hidden="true">&laquo;</span>\n\
                        </a>\n\
                    </li>';
    }

    pagination_parent_node.insertAdjacentHTML('beforeend',previous);

    if (next_state==true)
    {
        next = '<li class="page-item" id="next-li" >\n\
                    <a class="page-link" id="next-link" href="javascript:void(0);" onclick="pageBox('+next_page+'); return false;" aria-label="next">\n\
                        <span aria-hidden="true">&raquo;</span>\n\
                    </a>\n\
                </li>';
    }
    else
    {
        next = '<li class="page-item disabled" id="next-li" >\n\
                    <a class="page-link" id="next-link" href="#" tabindex="-1" aria-label="next">\n\
                        <span aria-hidden="true">&raquo;</span>\n\
                    </a>\n\
                </li>';
    }

    pagination_parent_node.insertAdjacentHTML('beforeend',next);

}

function pageBox(page) {
    const replyNode = document.querySelector(".reply-input");
    const resetReplyNode = document.querySelector(".comment-content");
    const newNode = replyNode.cloneNode(true);
    resetReplyNode.replaceChildren();
    resetReplyNode.insertAdjacentElement('beforeend',newNode);

    const pagination_parent_node = document.querySelector(".pagination");
    pagination_parent_node.replaceChildren();

    replyList(location.href,page);
}


function buildPagination(pagination) {
    const pages = pagination[0];
    const last_page = pages.num_pages;
    const current_page = pages.number;
    const max_page_index_numbers = 10;
    const middle_of_index_number = Math.ceil(Math.round(max_page_index_numbers/2));

    let min_page = '';
    let max_page = '';
    let page_range = '';

    let previous_state = '';
    let next_state = '';
    let pre_page = '';
    let next_page = '';

    if (current_page < middle_of_index_number){
        min_page = 1;
        max_page = Math.min(min_page + (max_page_index_numbers-1), last_page);
    }
    else
    {
        min_page = ((current_page-1)/max_page_index_numbers) * max_page_index_numbers +1 - (middle_of_index_number-1);
        min_page = Math.max(min_page, 1);
        max_page = Math.min(current_page + (middle_of_index_number), last_page);
    }

    page_range = range(min_page, max_page+1 );


    if (current_page == 1 ) //previous button disable
    {
        previous_state=false;
    }
    else
    {
        previous_state=true;
        pre_page=min_page-1;
    }

    if (current_page == last_page ) //next button disable
    {
        next_state=false;
    }
    else
    {
        next_state=true;
        next_page=max_page+1;
    }

    paginationArrowButton(previous_state,next_state,pre_page,next_page);

    const sibling_nodes = document.querySelector("#previous-li");
    let snippet = '';

    for (const page in page_range.reverse())
    {
        if (page_range[page]==current_page)
        {
            snippet = '<li class="page-item page-number active"><a class="page-link" href="javascript:void(0);" onclick="pageBox('+page_range[page]+'); return false;">'+page_range[page]+'</a></li>';
        }
        else
        {
            snippet = '<li class="page-item page-number"><a class="page-link" href="javascript:void(0);" onclick="pageBox('+page_range[page]+'); return false;">'+page_range[page]+'</a></li>';
        }
        sibling_nodes.insertAdjacentHTML('afterend',snippet);
    }

}


/*=====================================
window.addEventListener
======================================= */

window.addEventListener('DOMContentLoaded', function()
{
    // call replies list function
    if ((window.location.pathname).includes('detail'))
    {
        const check_class = document.querySelector('.comment-area');

        if (check_class)
        {
            replyList(location.href);
        }
    }
});