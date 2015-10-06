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

    $('.rate_radio', element).change(function(eventObject) {
	target_id = eventObject.target.id;
	vote = parseInt(target_id.split('_')[1]);
        $.ajax({
            type: "POST",
            url: vote_handler,
            data: JSON.stringify({"vote": vote}),
        });
	Logger.log("edx.ratexblock.likert_rate", {"vote":vote})
    });

    $('.rate_string_area', element).change(function(eventObject) {
	$('.rate_thank_you', element).css('visibility','hidden');
	var feedback_string = eventObject.currentTarget.value;
	Logger.log("edx.ratexblock.string_feedback", {"feedback":feedback_string})
        $.ajax({
            type: "POST",
            url: feedback_handler,
            data: JSON.stringify({"feedback": feedback_string}),
	    success: function() {$('.rate_thank_you', element).css('visibility','visible')},
        });
    });

}
