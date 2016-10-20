/*global $, document, alert */
$(document).ready(function () {
    'use strict';
    
});
var isChecked = false;

function check_groupid() {
    'use strict';
    var groupid = $('#groupid').val(), campidx = $('#campidx').val(), idRegex = /^[a-z]+[a-z0-9]{5,19}$/g;
    
    if (!idRegex.test(groupid)) {
        alert('아이디는 6~20자 알파벳, 숫자만 가능합니다.');
        isChecked = false;
        return;
    }
    
    $.ajax({
        url: './check-groupid',
        type: 'POST',
        data: 'groupid=' + groupid + '&campidx=' + campidx,
        success: function (data) {
            if (parseInt(data, 10) === 0) {
                alert("사용이 가능한 아이디입니다.");
                isChecked = true;
            } else {
                alert("사용이 불가한 아이디입니다.");
                isChecked = false;
            }
        }
    });
}



// 폼 검증 함수
function validate_form() {
    
    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/, contact = $('#leadercontact').val();
    
    // 이메일 중복검사
    if (!isChecked) {
        alert('아이디 중복 검사를 해주세요');
        return false;
    }
    
    // 비밀번호 공백
    if ($('#pwd').val() === '') {
        alert('비밀번호를 입력해 주세요');
        return false;
    }
    
    // 비밀번호 일치여부
    if ($('#pwd').val() !== $('#pwd2').val()) {
        alert('비밀번호가 일치하지 않습니다');
        return false;
    }
    
    // 단체 이름 입력 안함
    if ($('#name').val() === '') {
        alert('단체 이름을 입력해 주세요');
        return false;
    }
    
    // 담당자 이름 입력 안함
    if ($('#leadername').val() === '') {
        alert('담당자 이름을 입력해 주세요');
        return false;
    }
    
    // 연락처
    if (!contact_regex.test(contact)) {
        alert('올바른 연락처 정보를 입력해 주세요');
        return false;
    }
    
    return true;
}

function submit_form() {
    'use strict';
    if (validate_form()) {
        $('#form').submit();
    }
}