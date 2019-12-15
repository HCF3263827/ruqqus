$(function(){
    var kKeys = [];
    function Kpress(e){
        kKeys.push(e.keyCode);
        if (kKeys.toString().indexOf("38,38,40,40,37,39,37,39,66,65") >= 0) {
            $(this).unbind('keydown', Kpress);
            kExec();
        }
    }
    $(document).keydown(Kpress);
});
function kExec(){
   $('body').css('background').append ('<iframe width="0" height="0" src="https://www.youtube.com/embed/IZNHNrAIWps?rel=0&amp;controls=0&amp;showinfo=0&autoplay=1" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
   $('header').addClass('ruckus');
   $('a').addClass('ruckus');
   $('p').addClass('ruckus');
   $('img').addClass('ruckus');
};
