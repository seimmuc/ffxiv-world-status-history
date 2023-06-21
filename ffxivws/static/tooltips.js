function findChildTooltips(parent) {
  return $(parent).find('div.tooltip');
}

$(document).ready(function() {
  const tooltipElems = $('[tooltip-text]');
  tooltipElems.on('mouseenter', function() {
    findChildTooltips(this).remove();
    $(this).append(`<div class="tooltip">${$(this).attr('tooltip-text')}</div>`);
  });
  tooltipElems.on('mouseleave', function() {
    findChildTooltips(this).remove();
  });
  tooltipElems.on('mousemove', function(e) {
    const tooltip = findChildTooltips(this);
    const body = $('body');
    let x = Math.min(e.clientX, body.outerWidth(true) - tooltip.outerWidth(true));
    let y = Math.min(e.clientY, body.outerHeight(true) - tooltip.outerHeight(true));
    tooltip.css('left', `${x}px`).css('top', `${y}px`);
  });
});
