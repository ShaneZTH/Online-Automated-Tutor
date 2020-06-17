let acct_select = document.getElementById('account_type');
let major_select = document.getElementById('major').parentElement;
let year_select = document.getElementById('year').parentElement;

acct_select.onchange = function () {
    if($('#account_type').val()=='counselor'){
        $('#major.form-control').val('N/A');
        $('#major').attr('disabled', 'disabled');
        $('#major').prop('required',false);
        $('#year').val('N/A');
        $('#year').attr('disabled', 'disabled');
    } else {
        $('#major').val('');
        $('#major').removeAttr('disabled');
        $('#year').val('');
        $('#year').removeAttr('disabled');
    }
}