

/*=====================================
blog like event
======================================= */

const likeToggler = document.querySelector(".lni-heart");

likeToggler.addEventListener('click', async function() {
    const likeTogglerDiv = document.querySelector(".like-btn");
    const likeCount = document.querySelector(".like_count");

    const url = window.location.origin + '/opensource/like/json/'
    let post_num = window.location.href.split('/')
    post_num = post_num[post_num.length - 2]
    const full_url = url + post_num + '/'

    try {
        let res = await axios.get(full_url);
        likeCount.textContent=res.data.like_count;
        likeToggler.classList.toggle('clicked');
        likeTogglerDiv.setAttribute('onfocus','this.blur()');
        likeTogglerDiv.setAttribute('readonly',true);
    } catch (err){
        console.log('like error : ' ,err);
    }
})

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

    for (const reply in replies) {
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
                        <a class="btn btn-outline-primary btn-sm mx-3 " href="javascript:void(0);" onclick="createReplyBox(); return false;">Update</a> \n\
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


const replyList = async function(url) {
    try {
        const full_url = url+'reply/json/';
        let res = await axios.get(full_url);
        buildReplyStack(res.data,full_url);
    }
    catch (err){
        console.log('reply list error : ' ,err);
    }

}

/*=====================================
Create a reply to a blog
======================================= */

/*=====================================
Update a reply to a blog
======================================= */

/*=====================================
Delete a reply to a blog
======================================= */

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
            replyList(location.href)
        }
    }
});