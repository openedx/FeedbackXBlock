/* Javascript for FeedbackXBlock. */
// Work-around so we can log in edx-platform, but not fail in Workbench
if (typeof Logger === 'undefined') {
  var Logger = {
    log: function (a) {
      console.log(JSON.stringify(a) + '/' + JSON.stringify(a));
    }
  };
}

function FeedbackXBlock(runtime, element) {
  function getLikedVote() {
    if ($('.feedback_radio:checked', element).length === 0) {
      return -1;
    }

    return parseInt($('.feedback_radio:checked', element).attr('data-id').split('_')[1]);
  }

  function getFeedbackMessage() {
    return $('.feedback_freeform_area', element).val();
  }

  function updateVoteCount(data) {
    if (data.success && data.aggregate && $('.feedback_vote_count', element).length) {
      $('.feedback_vote_count', element).each(function (idx) {
        $(this).text('(' + data.aggregate[idx] + ')');
      });
    }
  }

  function submit_feedback(freeform, vote) {
    var feedback = {};
    if (freeform) {
      feedback['freeform'] = freeform;
    }
    if (vote !== -1) {
      feedback['vote'] = vote;
    }

    Logger.log('edx.feedbackxblock.submitted', feedback);
    $.ajax({
      type: 'POST',
      url: runtime.handlerUrl(element, 'feedback'),
      data: JSON.stringify(feedback),
      success: function (data) {
        $('.feedback_thank_you', element).text(data.response || '');
        updateVoteCount(data);
      }
    });
  }

  $('.feedback_submit_feedback', element).click(function () {
    submit_feedback(getFeedbackMessage(), -1);
  });

  $('.feedback_radio', element).change(function () {
    Logger.log('edx.feedbackxblock.likert_changed', { vote: getLikedVote() });
    submit_feedback(false, getLikedVote());
  });

  $('.feedback_freeform_area', element).change(function () {
    Logger.log('edx.feedbackxblock.freeform_changed', { freeform: getFeedbackMessage() });
  });
}
