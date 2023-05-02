$(document).ready(function() {
  // Temporarily disable timezone button transitions
  $('#timezone-form button').addClass('notransition');
  
  const selectElm = $('#timezone-form #timezone-selector');
  const updateBtn = $('#timezone-form #timezone-update-btn');
  const localBtn = $('#timezone-form #timezone-local-btn');

  const updateBtnWidth = updateBtn.outerWidth();
  // Un-hide local button to get its width, it will possibly get hidden again in selectElm.change handler
  localBtn.removeClass('hidden');
  const localBtnWidth = localBtn.outerWidth();
  const originalTz = selectElm.find(':selected[selected]').val();
  const savedTz = selectElm.attr('data-svtz');
  const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (localTz !== undefined && selectElm.find(`[value='${localTz}']`).length < 1) {
    localTz = undefined;
  }

  localBtn.click(e => {
    let option = selectElm.find(`[value='${localTz}']`).first();
    console.log(option);
    if (option.length) {
      selectElm.children('option').filter(function() {
        const o = $(this);
        o.prop('selected', o.val() == localTz);
      });
      selectElm.change();
    }
  });

  function setButtonState(button, enabled, width) {
    if (!button.prop('disabled') === enabled) {
      return;
    }
    button.prop('disabled', !enabled);
    if (!enabled) {
      button.css('width', 0).css('padding', '3px 0px').css('border-right', 'none').css('border-left', 'none');
    } else {
      button.css('width', width).css('padding', '3px 10px').css('border-right', '').css('border-left', '');
    }
  }

  selectElm.change(e => {
    const newOption = selectElm.find(':selected');
    
    // Update select element width
    const tempSelect = $(`<select id="timezone-selector"><option>${newOption.text()}</option></select>`);
    tempSelect.css('visibility', 'hidden').css('position', 'fixed');
    tempSelect.insertAfter(selectElm);
    const width = tempSelect.width();
    tempSelect.remove();
    selectElm.width(width);

    // Update button states
    setButtonState(updateBtn, newOption.val() !== originalTz, updateBtnWidth);
    setButtonState(localBtn, localTz !== undefined && newOption.val() !== localTz, localBtnWidth);
  });

  selectElm.change();
  setTimeout(() => {
    // Browsers cache DOM changes, so we have to delay re-enabling transitions
    $('#timezone-form button').removeClass('notransition');
  }, 1);
});