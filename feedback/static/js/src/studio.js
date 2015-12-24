function FeedbackBlock(runtime, element, data) {
    // When the user asks to save, read the form data and send it via AJAX
    $(element).find('.save-button').bind('click', function() {
	var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
	var form_data = {
	    likert: $(element).find('input[name=likert]').val(),
	    likert0: $(element).find('input[name=likert0]').val(),
	    likert1: $(element).find('input[name=likert1]').val(),
	    likert2: $(element).find('input[name=likert2]').val(),
	    likert3: $(element).find('input[name=likert3]').val(),
	    likert4: $(element).find('input[name=likert4]').val(),
	    freeform: $(element).find('input[name=freeform]').val(),
	    placeholder: $(element).find('input[name=placeholder]').val(),
	    icon_set: $(element).find('select[name=icon_set]').val()
	};
	runtime.notify('save', {state: 'start'});
	$.post(handlerUrl, JSON.stringify(form_data)).done(function(response) {
	    runtime.notify('save', {state: 'end'});
	});
    });

    // When the user hits cancel, use Studio's proprietary notify()
    // extension
    $(element).find('.cancel-button').bind('click', function() {
	runtime.notify('cancel', {});
    });

    // Select the right icon set in the dropdown
    $(element).find('select[name=icon_set]').val(data['icon_set']);
}
