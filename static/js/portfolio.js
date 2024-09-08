
"use strict";


function createTimeLine(data)
{
    const year_node = document.querySelector(".apland-timeline-area");
    let year = '';
    let timeline_year = '';
    let card = '';
    let collapse = '';
    let icon = '';

    for (const item in data)
    {
        if(year == '' )
        {
            year = data[item].start_year;

            timeline_year = '<!-- Single Timeline Content--><div class="single-timeline-area"><div class="timeline-date wow fadeInLeft" data-wow-delay="0.1s" style="visibility: visible; animation-delay: 0.1s; animation-name: fadeInLeft;"><p>Current</p></div><div class="row row-'+year+'"></div></div>';

            year_node.insertAdjacentHTML('beforeend',timeline_year);
        }
        else if(year != data[item].start_year)
        {
            year = data[item].start_year;
            timeline_year = '<!-- Single Timeline Content--><div class="single-timeline-area"><div class="timeline-date wow fadeInLeft" data-wow-delay="0.1s" style="visibility: visible; animation-delay: 0.1s; animation-name: fadeInLeft;"><p>'+year+'</p></div><div class="row row-'+year+'"></div></div>';

            year_node.insertAdjacentHTML('beforeend',timeline_year);
        }

        switch (data[item].color) {
            case 'orange':
                icon = '<i class="fa-regular fa-building"></i>';
                break;
            case 'red':
                icon = '<i class="fa-regular fa-clipboard"></i>';
                break;
            case 'pink':
                icon = '<i class="fa-solid fa-people-group"></i>';
                break;
            case 'yellow':
                icon = '<i class="fa-solid fa-laptop"></i>';
                break;
            case 'blue':
                icon = '<i class="fa-solid fa-bullhorn"></i>';
                break;
            case 'skyblue':
                icon = '<i class="fa-solid fa-chalkboard-user"></i>';
                break;
            case 'green':
                icon = '<i class="fa-solid fa-earth-americas"></i>';
                break;
            case 'gray':
                icon = '<i class="fa-solid fa-terminal"></i>';
                break;
            default :
                icon = '<i class="fa-solid fa-mug-hot"></i>';
        }


        card = '<div class="col-12 col-md-6 col-lg-4" ><div class="single-timeline-content d-flex wow fadeInLeft" data-bs-toggle="collapse" data-bs-target="#card'+data[item].pk+'" data-wow-delay="0.5s" style="visibility: visible; animation-delay: 0.3s; animation-name: fadeInLeft;"><div class="timeline-icon timeline-icon-'+data[item].color+'" >'+icon+'</div><div class="timeline-text">'+data[item].project_start_date+' - '+data[item].title+'<p>'+data[item].summary+'<p></div></div></div>';

        collapse = '<div class="collapse" id="card'+data[item].pk+'"><div class="card card-body">'+data[item].content+'</div></div>';


        const itemNode = document.querySelector(".row-"+year);
        itemNode.insertAdjacentHTML('beforeend',card+collapse);

    }


}

const workExperience = async function(url) {
    try {
        const full_url = url+'json/';
        let res = await axios.get(full_url);
        createTimeLine(res.data);
    }
    catch (err){
        console.log('get work experience data error : ' ,err);
    }

};


/*=====================================
window.addEventListener
======================================= */

window.addEventListener('DOMContentLoaded', function()
{
    workExperience(location.href);

    const event_modal = new bootstrap.Modal(document.getElementById('myModal'), {})
    console.log('event_modal :',event_modal)
    if (event_modal){
        event_modal.show();
    }
});