/**
 * Created by junwon on 2017. 2. 4..
 */
requirejs.config({
    shim : {
        "bootstrap" : { "deps" :['jquery'] }
    },
    paths: {
        "jquery" : "//code.jquery.com/jquery-2.1.1.min",
        "bootstrap" : "//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min",
        "ga": "//www.google-analytics.com/analytics"
    }
});
requirejs([
        "jquery",
        "bootstrap",
        "analytics"
    ],
    function($) {
        $(document).ready(function () {

        });
    }
);