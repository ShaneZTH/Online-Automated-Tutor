// html: academic-main-v2.html
// Serve for student's academic main page
var pathName = window.location.pathname.split("/");
var course = pathName[4].toString();

var unreadCount = document.getElementById("unread-posts-count");
var unreadBtn = document.getElementById("unread-posts-text");

var unansweredCount = document.getElementById("unanswered-posts-count");
var unansweredBtn = document.getElementById("unanswered-posts-text");

var questionBox = document.getElementById("student-question");
var answerBox = document.getElementById("student-answer");

// var unreadModal = document.getElementById("unreadModal");

var INDENT = "&nbsp;&nbsp;&nbsp;&nbsp;";

/*
 *  Initialization
 */

window.onload = function load_numbers() {
    console.log("Loading numbers...");

    get_unread_count(course);
    get_unanswered_count(course);
    get_answered_posts(course);
}

/*
 *   EventListeners
*/
// -------------------------------------------------------
// Sidebar
// -------------------------------------------------------
$("#bot-answer-feedback-satisfied").click(function () {
    console.log('bot-answer-feedback-satisfied is clicked');
    submitBotFeedback("satisfied");
    botAnswerFeedbackToggle(false);
});

$("#bot-answer-feedback-unsatisfied").click(function () {
    console.log('bot-answer-feedback-unsatisfied is clicked');
    submitBotFeedback("unsatisfied");
    botAnswerFeedbackToggle(false);
});


$("#btn-ask-a-question").click(function (event) {
    $("#answered-post-section").hide();
    $("#qna-section").show();
});

$("#posts-sidebar").on("click", "tr", function (event) {
    var post = $(this)
    console.log("posts-sidebar click", post);
    var title = $(this).find('.answered-post-title').text().trim();
    var body = $(this).find('.answered-post-body').text().trim();

    console.log('title', title);
    console.log('body', body);

    $("#answered-post-question").val(title);
    $("#answered-post-answer").val(body);
    $("#qna-section").hide();
    $("#answered-post-section").show();
});

// -------------------------------------------------------

// -------------------------------------------------------

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
    console.log("count_unanswered() settings: ", settings);
    $.ajax(settings).done(function (response) {
        console.log("Response", response);
        refreshUnreadPostModal(course, qid);
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


questionBox.addEventListener('keypress', (e) => {
    if (e.code == 'Enter' || e.code == 'NumpadEnter') {
        console.log('Got keystroke ' + e.code);
        if (e.shiftKey) {
            e.stopPropagation();
        } else {
            e.preventDefault();
            if ($("#qna-default-center").is(':visible')) {
                getAnswer();
            } else {
                $("#bot-answer-feedback-satisfied").click();
            }
        }
    }
});

// -------------------------------------------------------

function submitBotFeedback(feedback) {
    var settings = {
        "url": "/academic/api/v1/bot-answer-feedback",
        "method": "POST",
        "timeout": 0,
        "data": {
            "feedback": feedback,
        },
        statusCode: {
            200: function () { // Satisfied request successfully sent
                alert("Thank you for your response");
                get_answered_posts(course);
            },
            201: function () { // Unsatisfied request successfully sent
                alert("Thank you for your response. Question has been reported to tutors.");
                refreshCounts(course);
            }
        }
    }

    console.log("submitBotFeedback settings: ", settings);
    $.ajax(settings).done(function () {
        console.log("submitBotFeedback() Success", feedback)
        // console.log(questionBox.value, answerBox.value);
        // answerBox.value = "";
        // questionBox.value = "";
        // console.log(questionBox.value, answerBox.value);
    });
    return;
}

function botAnswerFeedbackToggle(t) {
    if (t) {
        $("#qna-default-center").hide();
        $("#bot-answer-feedback").show();
        return true;
    } else {
        $("#bot-answer-feedback").hide();
        $("#qna-default-center").show();
        return false;
    }
    return
}


// -------------------------------------------------------

function refreshUnreadPostModal(course, pid) {
    console.log(course, pid);

    var settings = {
        "url": "/academic/api/v1/get/question/current-qid",
        "method": "GET",
        "timeout": 0
    }
    $.ajax(settings).done(function (response) {
        console.log("Success - refreshUnreadPostModal()", response);

        var q = INDENT + response["question"];
        var a = INDENT + response["answer"];

        $(".unread-status-block").find(".question-content p").html(q);
        $(".unread-status-block").find(".answer-content p").html(a);

    });
}

function tutorAnswerFeedback(feedback) {
    console.log("tutorAnswerFeedback get: ", feedback);

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
        refreshCounts(course);
        get_answered_posts(course);
        $("#unreadPostModal").modal("hide");
    });

}

function get_answered_posts(course) {
    var settings = {
        "url": "/academic/api/v1/posts/answered",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }

    $.ajax(settings).done(function (response) {
        var r_js = JSON.parse(response);
        var r_len = r_js.length;

        // Clear of the pre-existing sidebar content
        $("#posts-sidebar").empty();

        for (let i = 0; i < r_len; i++) {
            var post = "<tr><td><div><h5 class=\"answered-post-title mb-0\" data-pats=\"post-title\">" + r_js[i]["problem"] + "</h5>" +
                "<p class=\"answered-post-body mb-0\" data-pats=\"post-body\">" + INDENT + r_js[i]['answer'] +
                "<span class=\"glyphicon glyphicon-menu-right pull-right\" aria-hidden=\"true\"></span>" +
                "</p></div></td></tr>";
            // console.log(i, post);
            $("#posts-sidebar").append(post);
        }
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

            var post = "<tr>\n" +
                "<td>#" + r_js[i]['qid'] + "</td>\n" +
                " <td class=\"post-content\">" + r_js[i]['post'] + "\n" +
                " </td>\n" +
                "</tr>";
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
        // console.log("unanswered-posts success!", response);
        var r_js = JSON.parse(response);
        var r_len = r_js.length;
        // console.log("response length", r_len);
        for (let i = 0; i < r_len; i++) {
            // console.log("i", r_js[i]);

            var post = "<tr>\n" +
                "<td>#" + r_js[i]['qid'] + "</td>\n" +
                " <td class=\"post-content\">" + r_js[i]['post'] + "\n" +
                " </td>\n" +
                "</tr>";

            // console.log(post);
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
        "async": false,
        "timeout": 0,
        "data": {
            "course": course,
            "question": userQuestion
        },
        statusCode: {
            "208": function (response) { // Answer exists in the DB
                console.log("208 found");
                AnswerBox.value = response;
                refreshCounts(course);

                botAnswerFeedbackToggle(true);
                // TODO: After feedback is received, toggle to false
            },
            "201": function (response) { // New question,
                console.log("201 found");
                AnswerBox.value = response;
                refreshCounts(course);
            }
        }
    };

    $.ajax(settings);
    // console.log("getAnswer() settings: ", settings);
    // $.ajax(settings).done(function (response) {
    //     // console.log("success!", response);
    //     AnswerBox.value = response;
    //     get_unread_count(course);
    //     get_unanswered_count(course);
    // });
}

function refreshCounts(c) {
    get_unread_count(c);
    get_unanswered_count(c);
}