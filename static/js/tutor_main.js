// html: tutor-main-v1.html
var pathName = window.location.pathname.split("/");
var course = pathName[4].toString();

var unansweredBtn = document.getElementById("unanswered-questions-text")
var unansweredCount = document.getElementById("unanswered-questions-count");

var incomingQuestions = document.getElementById("unanwered-questions");

var answerBox = document.getElementById("tutor-answer-box");

window.onload = function() {
    console.log("Loading page...");
    get_course_unanswered_count(course);
}

unansweredBtn.onclick = function() {
    console.log("unansweredBtn is clicked");
    $("#unanswered-questions").empty();
    get_course_unanswered_questions(course);
}

function get_course_unanswered_questions(course) {
    console.log("get_course_unanswered_questions", course);
    var settings = {
        "url": "/academic/api/v1/tutor/course-unanswered-questions",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }
    $.ajax(settings).done(function (response) {
        console.log("tutor-unanswered-questions success!", response);
        var r_js = JSON.parse(response);
        var r_len = r_js.length;
        for (let i = 0; i < r_len; i++) {
            console.log("i", r_js[i]);

            var post = "<tr>\n" +
                "<td>#" + (i+1) + "</td>\n" +
                " <td>" + r_js[i]['post'] + "\n" +
                " </td>\n" +
                "</tr>";
            console.log(post);
            $("#unanswered-questions").append(post);
        }
    });
}

function get_course_unanswered_count(course) {
    console.log("get_course_unanswered_count", course);
    var settings = {
        "url": "/academic/api/v1/tutor/course-unanswered-count",
        "method": "POST",
        "timeout": 0,
        "data": {
            "course": course
        }
    }
    console.log("count_unanswered() settings: ", settings);
    $.ajax(settings).done(function (response) {
        console.log("unanswered success!", response);
        unansweredCount.textContent = response;
    });
}

function submitAnswer(){
    console.log("Submitting Answer...");
}

