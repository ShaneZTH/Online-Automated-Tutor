// var pathName = url.pathName.split("\\");
var pathName = window.location.pathname.split("/");
var course = pathName[4].toString();

var unreadCount = document.getElementById("unread-posts-count");
var unreadBtn = document.getElementById("unread-posts-text");

var unansweredCount = document.getElementById("unanswered-posts-count");
var unansweredBtn = document.getElementById("unanswered-posts-text");

var questionBox = document.getElementById("student-question");

unreadBtn.onclick = function () {
    console.log("unreadBtn is clicked");
}


window.onload = function load_numbers() {
    console.log("Loading numbers...");

    get_unanswered_count(course);
    get_unread_count(course);
}

questionBox.addEventListener('keypress', (e) => {
    // console.log('Got keystroke ' + e.code);
    if (e.code == 'Enter') {
        if (e.shiftKey) {
            e.stopPropagation();
        } else {
            e.preventDefault();
            getAnswer();
        }
    }
});

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

function getAnswer() {
    var AnswerBox = document.getElementById("student-answer");
    AnswerBox.textContent = "";

    var userQuestion = $("#student-question").val();
    console.log("student's question: ", userQuestion)

    var settings = {
        "url": "/academic/api/v1/answer",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course,
            "question": userQuestion
        },
    };

    // console.log("getAnswer() settings: ", settings);
    $.ajax(settings).done(function (response) {
        // console.log("success!", response);
        AnswerBox.textContent = response;
    });
}