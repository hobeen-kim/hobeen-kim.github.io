$('.button-posts').click(function(){
    $(this).addClass('selected');
    $('.button-series').removeClass('selected');
    $('.categorylist-series').addClass('categorylist-hide');
    $('.categorylist-posts').removeClass('categorylist-hide');
});

$('.button-series').click(function(){
    $(this).addClass('selected');
    $('.button-posts').removeClass('selected');
    $('.categorylist-posts').addClass('categorylist-hide');
    $('.categorylist-series').removeClass('categorylist-hide');
});