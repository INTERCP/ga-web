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
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/, birth_regex = /^(19([0-9]{2})|200([0-9])|201([0-5]))-?(0([1-9])|1[0-2])-?([0-2][0-9]|[3][0-1])$/g;

    
    // 비밀번호 공백
    if ($('#pwd').val() !== '') {
        // 비밀번호 일치여부
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
    
    // 지부 선택 안함
    if ($('#area_idx').val() === '') {
        alert('지부를 선택해 주세요');
        return false;
    }
    
    // 성별 선택 안함
    if ($('input[name=sex]:checked').val() === undefined) {
        alert('성별을 선택해 주세요');
        return false;
    }
    
    // 생년월일
    if (!birth_regex.test($('#birth').val())) {
        alert('생년월일을 올바르게 선택해 주세요');
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
    
    // 참가 구분
    if ($('input[name=persontype]:checked').val() === undefined) {
        alert('참가구분을 선택해 주세요');
        return false;
    }
    
    // 단체버스
    if ($('input[name=bus_yn]:checked').val() === undefined) {
        alert('단체버스 이용 여부를 선택해 주세요');
        return false;
    }
    
    // MIT 참가 여부
    if ($('input[name=mit_yn]:checked').val() === undefined) {
        alert('MIT참가 여부를 선택해 주세요');
        return false;
    }
    
    // 뉴커머 여부
    if ($('input[name=newcomer_yn]:checked').val() === undefined) {
        alert('선캠 처음 참석 여부를 선택해 주세요');
        return false;
    }
    
    if ($('input[type=checkbox]:checked').val() === undefined) {
        alert('인터콥 훈련여부를 적어도 하나 이상 체크해 주세요');
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