

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

function setReplyLocation(snippet){

}

function buildReplyStack(replies){

    for (const reply in replies) {
        snippet = '';

        if (comment.depth == 0)
        {
            snippet += '<div class="single-comment"></div>\n';
        }
        else if (comment.depth == 1)
        {
            snippet += '<div class="single-comment fist-reply"></div>\n';
        }
        else
        {
            snippet += '<div class="single-comment second-reply"></div>\n';
        }

        // thembnail
        snippet += '<div class="author-info"> \n\
                       <div class="thumb"> \n\
                        <img src="'+ replies[reply].thumbnail +'" alt="Image"> \n\
                    </div>\n';

        // name
        snippet += '<div class="author-details reply-{{comment.pk}}">\n\
                    <ul>\n\
                        <li class="name" id="name">{{comment.author}}</li>\n\
                        <li class="meta-date ms-2" id="{{comment.pk}}">{{comment.updated_at}}</li>\n\
                    </ul>\n';

        // comment
        snippet += '<p>{{comment.comment|safe}}</p>\n'

        //update, delete button
        snippet +=  '<div class="d-flex justify-content-end"> \n\
                        <a class="btn btn-outline-primary btn-sm mx-3 " href="javascript:void(0);" onclick="CreateReplyBox(); return false;">Update</a> \n\
                        <a class="btn btn-outline-secondary btn-sm mx-3" href="{% url 'blog:opensource_reply_delete' comment.pk%}">Delete</a> \n\
                    </div>\n'

        //reply button
        snippet +=  '<div class="d-flex justify-content-end mt-3"> \n\
                        <a class="btn btn-outline-danger btn-sm mx-3" href="javascript:void(0);"  onclick="NewReplyBox({{comment.pk}},{{comment.depth}}); return false;">Reply</a>\n\
                    </div>\n'

        // close brackets
        snippet += '        </div> \n\
                        </div> \n\
                    </div>\n'


        console.log('snippet : ',snippet);
    }
}


const replyList = async function(url) {
    try {
        const full_url = url+'reply/json/';
        let res = await axios.get(full_url);
        buildReplyStack(res.data);
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