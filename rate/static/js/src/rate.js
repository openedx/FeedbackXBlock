/* Javascript for RateXBlock. */
// Work-around so we can log in edx-platform, but not fail in Workbench
if (typeof Logger === 'undefined') {
    var Logger = {
        log: function(a, b) { 
	    console.log(JSON.stringify(a)+"/"+JSON.stringify(a));
	}
    };
}

function RateXBlock(runtime, element) {
    function likert_vote() {
	var vote = 0;
	if ($(".rate_radio:checked", element).length === 0) {
	    vote = -1;
	} else {
	    vote = parseInt($(".rate_radio:checked", element).attr("id").split("_")[1]);
	}
	return vote;
    }

    function feedback() {
	return $(".rate_freeform_area", element).val();
    }

    function submit_feedback(freeform, vote) {
	var feedback = {};
	if(freeform) {
	    feedback['freeform'] = freeform;
	}
	if(vote != -1) {
	    feedback['vote'] = vote;
	}

	Logger.log("edx.ratexblock.submitted", feedback);
	$.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'feedback'),
            data: JSON.stringify(feedback),
	    success: function(data) {
		$('.rate_thank_you', element).text("");
		$('.rate_thank_you', element).text(data.response);
	    }
        });
    }

    $(".rate_submit_feedback", element).click(function(eventObject) {
	submit_feedback(feedback(), -1);
    });

    $('.rate_radio', element).change(function(eventObject) {
	Logger.log("edx.ratexblock.likert_changed", {"vote":likert_vote()});
	submit_feedback(false, likert_vote());
    });

    $('.rate_freeform_area', element).change(function(eventObject) {
	Logger.log("edx.ratexblock.freeform_changed", {"freeform":feedback()});
    });
}
