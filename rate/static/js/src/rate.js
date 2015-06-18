/* Javascript for RateXBlock. */
var x;

function RateXBlock(runtime, element) {
    var vote_handler = runtime.handlerUrl(element, 'vote');
    var feedback_handler = runtime.handlerUrl(element, 'feedback');

    $('.rate_likert_rating', element).click(function(eventObject) {
	vote_class = eventObject.currentTarget.className.split(' ').find(function f(x) { return x.startsWith("rate_rating_") } )
	vote = parseInt(vote_class.split('_')[2]);
	$('.rate_rating_active', element).removeClass("rate_rating_active");
	$('.'+vote_class, element).addClass("rate_rating_active");
	
        $.ajax({
            type: "POST",
            url: vote_handler,
            data: JSON.stringify({"vote": vote}),
        });
    });

    $('.rate_string_area', element).change(function(eventObject) {
	$('.rate_thank_you', element).css('visibility','hidden');
        $.ajax({
            type: "POST",
            url: feedback_handler,
            data: JSON.stringify({"feedback": eventObject.currentTarget.value}),
	    success: function() {$('.rate_thank_you', element).css('visibility','visible')},
        });
    });

}


/*
    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    

*/
