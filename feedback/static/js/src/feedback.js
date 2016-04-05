/* Javascript for FeedbackXBlock. */
// Work-around so we can log in edx-platform, but not fail in Workbench
if (typeof Logger === 'undefined') {
    var Logger = {
        log: function(a, b) { 
	    console.log(JSON.stringify(a)+"/"+JSON.stringify(a));
	}
    };
}

function FeedbackXBlock(runtime, element) {
    function likert_vote() {
	var vote = 0;
	if ($(".feedback_radio:checked", element).length === 0) {
	    vote = -1;
	} else {
	    vote = parseInt($(".feedback_radio:checked", element).attr("data-id").split("_")[1]);
	}
	return vote;
    }

    function feedback() {
	return $(".feedback_freeform_area", element).val();
    }

    function submit_feedback(freeform, vote) {
	var feedback = {};
	if(freeform) {
	    feedback['freeform'] = freeform;
	}
	if(vote != -1) {
	    feedback['vote'] = vote;
	}

	Logger.log("edx.feedbackxblock.submitted", feedback);
	$.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'feedback'),
            data: JSON.stringify(feedback),
	    success: function(data) {
		$('.feedback_thank_you', element).text("");
		$('.feedback_thank_you', element).text(data.response);
	    }
        });
    }

    $(".feedback_submit_feedback", element).click(function(eventObject) {
	submit_feedback(feedback(), -1);
    });

    $('.feedback_radio', element).change(function(eventObject) {
	Logger.log("edx.feedbackxblock.likert_changed", {"vote":likert_vote()});
	submit_feedback(false, likert_vote());
    });

    $('.feedback_freeform_area', element).change(function(eventObject) {
	Logger.log("edx.feedbackxblock.freeform_changed", {"freeform":feedback()});
    });
}
