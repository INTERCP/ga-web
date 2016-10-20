/*global $, document, alert */
$(document).ready(function () {
    'use strict';
    $('#bubun').hide();
    $('.pastor-type').show();
    $('.non-pastor-type').hide();
    
    // 참가형태 == 부분참가 일때 참가기간 선택 보여줌
    // 그 외는 모두 숨김
    $('input[name=fullcamp_yn]').change(function () {
        if ($(this).val() === '0') {
            $('#bubun').show();
        } else {
            $('#bubun').hide();
        }
    });
    
    $('.membership').change(function () {
        if ($('#none').is(':checked')) {
            $('#none').attr('checked', false);
        }
    });
    
    $('#none').change(function () {
        if ($('#none').is(':checked')) {
            $('.membership').attr('checked', false);
            $('#none').attr('checked', true);
        }
    });
    
});


// 폼 검증 함수
function validate_form() {
    
    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/i, contact = $('#hp').val() + '-' + $('#hp2').val() + '-' + $('#hp3').val();
    
    if (!contact.match(/undefined/)) {
        $('#contact').val(contact);
    }
    
    // 비밀번호 일치여부
    if ($('#pwd').val() !== '') {
        if ($('#pwd').val() !== $('#pwd2').val()) {
            alert('비밀번호가 일치하지 않습니다');
            return false;
        }
    }
    
    // 이름 입력 안함
    if ($('#name').val() === '') {
        alert('이름을 입력해 주세요');
        return false;
    }
    
    // 성별 선택 안함
    if ($('input[name=sex]:checked').val() === undefined) {
        alert('성별을 선택해 주세요');
        return false;
    }
    
    // 연락처
    if (!contact_regex.test($('#contact').val())) {
        alert('올바른 연락처 정보를 입력해 주세요');
        return false;
    }
    
    // 소속교회
    if ($('#church').val() === '') {
        alert('소속 교회를 입력해 주세요');
        return false;
    }
    
    if ($('#job').val() === '') {
        alert('직분을 선택해 주세요');
        return false;
    }
    
    // MIT 참가 여부 --> 3차캠프 참가여부
    /*
    if ($('input[name=mit_yn]:checked').val() === undefined) {
        alert('3차캠프 참가 여부를 선택해 주세요');
        return false;
    }
    */
    
    if ($('input[type=checkbox]:checked').val() === undefined) {
        alert('컨퍼런스 참여 경로를 적어도 하나 이상 체크해 주세요');
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