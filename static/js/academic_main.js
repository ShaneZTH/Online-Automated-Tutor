// html: academic-main-v2.html
// Serve for student's academic main page
var pathName = window.location.pathname.split("/");
var course = pathName[4].toString();

var unreadCount = document.getElementById("unread-posts-count");
var unreadBtn = document.getElementById("unread-posts-text");

var unansweredCount = document.getElementById("unanswered-posts-count");
var unansweredBtn = document.getElementById("unanswered-posts-text");

var questionBox = document.getElementById("student-question");

// var unreadModal = document.getElementById("unreadModal");


$("#unread-posts").on("click", "tr", function (event) {
    // > td.post-content
    var post = $(this)
    var qid = post.children("td:first-child").text().substring(1);
    var qText = post.children(".post-content").text();
    console.log("unread-posts click", qid, qText);

    var settings = {
        "url": "/academic/api/v1/set/current-qid",
        "method": "POST",
        "timeout": 0,
        "data": {
            "qid": qid
        }
    }
    // console.log("count_unanswered() settings: ", settings);
    $.ajax(settings).done(function (response) {
        console.log(response);
    });

    $("#unreadModal").modal("hide");
    $("#unreadPostModal").modal("show");

});

$("#unanswered-posts").on("click", "tr > td.post-content", function (event) {
    alert($(this).text());
});


unreadBtn.onclick = function () {
    console.log("unreadBtn is clicked");
    /* Notify backend that the Post being selected*/
    $("#unread-posts").empty();
    get_unread_posts(course);

}

unansweredBtn.onclick = function () {
    event.preventDefault();
    console.log("unansweredBtn is clicked");
    $("#unanswered-posts").empty();
    get_unanswered_posts(course);

}


window.onload = function load_numbers() {
    console.log("Loading numbers...");

    get_unread_count(course);
    get_unanswered_count(course);
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

function unreadFeedback(feedback) {
    console.log("unreadFeedback get: ", feedback);

    var settings = {
        "url": "/academic/api/v1/post/unread-feedback",
        "method": "POST",
        "timeout": 0,
        "data": {
            "feedback": feedback
        }
    }
    $.ajax(settings).done(function (response) {
        console.log("200-uf");
        // recount the number after the post is processed
        get_unread_count(course);
        $("#unreadPostModal").modal("hide");
    });

}

function get_unread_posts(course) {
    var settings = {
        "url": "/academic/api/v1/posts/unread",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }
    // console.log("count_unanswered() settings: ", settings);
    $.ajax(settings).done(function (response) {
        console.log("unread-posts success!", response);
        var r_js = JSON.parse(response);
        var r_len = r_js.length;
        for (let i = 0; i < r_len; i++) {
            console.log("i", r_js[i]);

            var post = "<tr>\n" +
                "<td>#" + r_js[i]['qid'] + "</td>\n" +
                " <td class=\"post-content\">" + r_js[i]['post'] + "\n" +
                " </td>\n" +
                "</tr>";
            console.log(post);
            $("#unread-posts").append(post);
        }
    });
}

function get_unanswered_posts(course) {
    var settings = {
        "url": "/academic/api/v1/posts/unanswered",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }
    // console.log("count_unanswered() settings: ", settings);
    $.ajax(settings).done(function (response) {
        console.log("unanswered-posts success!", response);
        var r_js = JSON.parse(response);
        var r_len = r_js.length;
        console.log("response length", r_len);
        for (let i = 0; i < r_len; i++) {
            console.log("i", r_js[i]);

            var post = "<tr>\n" +
                "<td>#" + r_js[i]['qid'] + "</td>\n" +
                " <td class=\"post-content\">" + r_js[i]['post'] + "\n" +
                " </td>\n" +
                "</tr>";
            console.log(post);
            $("#unanswered-posts").append(post);
        }
    });
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
        // console.log("unanswered success!", response);
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
        get_unread_count(course);
        get_unanswered_count(course);
    });
}