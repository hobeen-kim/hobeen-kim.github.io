$('.button-first').click(function(){
    $(this).addClass('selected');
    $('.button-second').removeClass('selected');
    $('.toggle-second').addClass('toggle-hide');
    $('.toggle-first').removeClass('toggle-hide');
});

$('.button-second').click(function(){
    $(this).addClass('selected');
    $('.button-first').removeClass('selected');
    $('.toggle-first').addClass('toggle-hide');
    $('.toggle-second').removeClass('toggle-hide');
});