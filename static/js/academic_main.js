
// var pathName = url.pathName.split("\\");
var pathName = window.location.pathname.split("/");

var unreadCount = document.getElementById("unread-posts-count");
var unreadBtn = document.getElementById("unread-posts-text");

var unansweredCount = document.getElementById("unanswered-posts-count");
var unansweredBtn = document.getElementById("unanswered-posts-text");

unreadBtn.onclick = function () {
    console.log("unreadBtn is clicked");
}


window.onload = function load_numbers() {
    console.log("Loading numbers...");
    var course = pathName[4].toString();

    get_unanswered_count(course);
    get_unread_count(course);
}

function get_unanswered_count(course) {
    var settings = {
        "url": "/academic/api/v1/count-unanswered",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }
    // console.log("count_unanswered() settings: ", settings);
    $.ajax(settings).done(function (response) {
        // console.log("success!", response);
        unansweredCount.textContent = response;
    });
}

function get_unread_count(course) {
    var settings = {
        "url": "/academic/api/v1/count-unread",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }
    // console.log("count_unread() settings: ", settings);
    $.ajax(settings).done(function (response) {
        // console.log("success!", response);
        unreadCount.textContent = response;
    });
}
