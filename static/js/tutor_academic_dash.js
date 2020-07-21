// HTML:tutor_academic_dash.html

// Load courses options based on USER's major
window.onload = function load_course() {
    var settings = {
        "url": "/academic/v1/user/major-courses",
        "method": "GET",
        "timeout": 0,
        "headers": {}
    };

    console.log("Major-Courses: ", settings);
    var courses, major;
    $.ajax(settings).done(function (response) {
        console.log("Response", response);
        major = response["major"].toUpperCase();
        courses = response["courses"];
        console.log("major", major)
        console.log("Courses", courses)
        for (const c in courses) {
            console.log(`Adding course-${courses[c]}`);
            var new_course = "<li><a href=\"/academic/api/v1/" + major + courses[c] + "/tutor\">" +
                "<button type=\"button\" class=\"btn btn-default\">" + major + " " + courses[c] + "</button>" +
                "</a></li>";
            $("#course-group").append(new_course);
        }
    });
}