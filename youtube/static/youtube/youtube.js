/*global $*/

(function() {
    "use strict";

    $(function() {
        $('.thumbnail').error(function() {
            $(this).hide();
            $(this).unbind();
            $(this).attr('src', '/static/youtube/missing.png');
        });
    });
})();
