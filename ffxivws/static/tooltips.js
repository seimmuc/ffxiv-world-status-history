function findChildTooltips(parent) {
  return $(parent).find('div.tooltip');
}

$(document).ready(function() {
  const tooltipElems = $('[tooltip-text]');
  tooltipElems.hover(
    function() {
      findChildTooltips(this).remove();
      $(this).append(`<div class="tooltip">${$(this).attr('tooltip-text')}</div>`);
    }, function() {
      findChildTooltips(this).remove();
    }
  );
  tooltipElems.mousemove(function(e) {
    findChildTooltips(this).css('left', `${e.pageX}px`).css('top', `${e.pageY}px`)
  });
});
