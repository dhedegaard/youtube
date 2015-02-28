/*global $*/

(function() {
    "use strict";
    $(function() {
        $.each($('.uploaded'), function(_, elem) {
            var $this = $(this);
            $this.text(moment($this.data('uploaded')).fromNow());
        });
    });
})();