let acct_select = document.getElementById('account_type');
let major_select = document.getElementById('major').parentElement;
let year_select = document.getElementById('year').parentElement;

// window.onload = function () {
//      $('#year').attr('disabled', 'disabled');
//      $('#major').attr('disabled', 'disabled');
//      $('#course').attr('disabled', 'disabled');
// }

acct_select.onchange = function () {
    if ($('#account_type').val() == 'counselor') {
        // $('#major.form-control').val('N/A');
        // $('#major').attr('disabled', 'disabled');
        // $('#major').prop('required', false);
        $('#major').val('N/A');
        $('#major').attr('disabled', 'disabled');
        $('#year').val('N/A');
        $('#year').attr('disabled', 'disabled');
        $('#course').val('N/A')
        $('#course').attr('disabled', 'disabled')
    } else if ($('#account_type').val() == 'tutor') {
        // $('#major').val('N/A');
        // $('#major').prop('required', false);
        // $('#major').attr('disabled', 'disabled');
        $('#major').removeAttr('disabled');

        $('#year').val('N/A');
        // $('#year').prop('required', false);
        $('#year').attr('disabled', 'disabled');

        $('#course').removeAttr('disabled');
    } else { // Student
        $('#major').val('');
        $('#major').removeAttr('disabled');
        $('#year').val('');
        $('#year').removeAttr('disabled');
        // $('#year').prop('required', false);
        $('#course').val('N/A');
        $('#course').attr('disabled', 'disabled');
        // $('#course').prop('required', false);
    }
}