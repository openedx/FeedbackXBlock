/* Javascript for RateXBlock. */
// Work-around so we can log in edx-platform, but not fail in Workbench
if (typeof Logger === 'undefined') {
    var Logger = {
        log: function(a, b) { 
	    console.log("<<Log>>"); 
	    console.log(a);
	    console.log(b);
	    console.log("<</Log>>"); 
	}
    }
}


function RateXBlock(runtime, element) {
    var vote_handler = runtime.handlerUrl(element, 'vote');
    var feedback_handler = runtime.handlerUrl(element, 'feedback');

    $('.rate_likert_rating', element).click(function(eventObject) {
	var vote_class = eventObject.currentTarget.className.split(' ').find(function f(x) { return x.startsWith("rate_rating_") } )
	var vote = parseInt(vote_class.split('_')[2]);
	$('.rate_rating_active', element).removeClass("rate_rating_active");
	$('.'+vote_class, element).addClass("rate_rating_active");
	
	Logger.log("edx.recommender.likert_rate", {"vote":vote})

        $.ajax({
            type: "POST",
            url: vote_handler,
            data: JSON.stringify({"vote": vote}),
        });
    });

    $('.rate_string_area', element).change(function(eventObject) {
	$('.rate_thank_you', element).css('visibility','hidden');
	var feedback_string = eventObject.currentTarget.value;
	Logger.log("edx.recommender.string_feedback", {"feedback":feedback_string})
        $.ajax({
            type: "POST",
            url: feedback_handler,
            data: JSON.stringify({"feedback": feedback_string}),
	    success: function() {$('.rate_thank_you', element).css('visibility','visible')},
        });
    });

}


/*
    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    

*/
