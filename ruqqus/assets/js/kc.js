var keys = [];
    var kcode = '38,38,40,40,37,39,37,39,66,65';

    $(document).keydown(function(e){
        keys.push( e.keyCode );
        if ( keys.toString().indexOf( kcode ) >=0 ){

            keys = [];

            //add music in background
           $('body').css('background', '#703bf7').append ('<iframe width="0" height="0" src="https://www.youtube.com/embed/IZNHNrAIWps?rel=0&amp;controls=0&amp;showinfo=0&autoplay=1" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
          //add &autoplay=1 at the end of the source link
        }
    });
