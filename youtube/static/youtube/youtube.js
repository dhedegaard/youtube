/*global $*/

(function() {
    "use strict";

    $(function() {
        console.log('proc1');
        $('.thumbnail').error(function() {
            console.log('proc');
            $(this).hide();
            $(this).unbind();
            $(this).attr('src', '/static/youtube/missing.png');
        });

        $.each($('.thumbnail'), function(_, e) {
            console.log(e.complete);
        });
    });
})();
