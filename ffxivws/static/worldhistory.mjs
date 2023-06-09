const STATE_ATTRIBUTES = ['status', 'classification', 'charcreate'];
let barBlockPopup = undefined;
let worldStates = undefined;

function dateOnlyISOString(date) {
  return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
}

function createPopup(worldId, attrType, date, snapshotIds, blockTag, snapsUrlBase) {
  const snapData = new Map(snapshotIds.map(id => [id, worldStates[worldId][id][attrType]]));
  const attrValues = new Set(snapData.values());
  const newPopup = $(`<div class="details-popup"><p class="details-date"><time datetime="${dateOnlyISOString(date)}">${date.toLocaleDateString()}</time></p></div>`);
  if (attrValues.size == 1) {
    newPopup.append(`<p class="details-value">${attrValues.values().next().value}</p>`);
  }
  const snapsList = $('<ol class="snapshot-list"></ol>');
  if (snapData.size) {
    for (const [sid, sdata] of snapData.entries()) {
      snapsList.append($(`<li><a class="snapshots-link" href="${snapsUrlBase.replaceAll("12345", sid.toString())}">Snapshot ${sid}${attrValues.size != 1 ? ' (' + sdata + ')' : ''}</a></li>`));
    }
  } else {
    snapsList.append($('<li><a>No snapshots</a></li>'));
  }
  snapsList.appendTo(newPopup);
  // Position the popup with CSS
  const blockPos = blockTag.position();
  newPopup.css({top: blockPos.top + blockTag.outerHeight(true), left: blockPos.left - 5});
  return newPopup;
}
function openPopup(popupTag, blockTag, click) {
  if (blockTag.hasClass('today')) {
    blockTag.css('transform', 'none');  // Transform breaks position and z-index for some reason
  }
  blockTag.append(popupTag);
  barBlockPopup = {popupTag: popupTag, parentTag: blockTag, click: click};
}
function closePopup() {
  if (barBlockPopup !== undefined) {
    barBlockPopup.popupTag.remove();
    if (barBlockPopup.parentTag.hasClass('today')) {
      barBlockPopup.parentTag.css('transform', '');
    }
    barBlockPopup = undefined;
  }
}

export default function init(worldStateData, snapsUrlBase) {
  if (worldStates !== undefined) {
    throw Error('World history module was already initialized!')
  }
  // Iterate over all world sections
  const worldSections = $('.history-bars-section');
  worldSections.each(function() {
    const worldSectionTag = $(this);
    const worldId = worldSectionTag.attr('world-id');
    // Iterate over all bar lines in the section
    const barBlocks = $('ol.history-bar > li.history-bar-line', worldSectionTag);
    barBlocks.each(function() {
      const blockTag = $(this);
      const snapshotIds = blockTag.attr('all-snapshots').split(',').filter(s => s.trim());
      const date = new Date(`${blockTag.attr('day')}T00:00:00`);  // date-time form must be used so that browser assumes local time instead of UTC
      const attrType = Array.from(this.parentElement.classList).find(c => STATE_ATTRIBUTES.includes(c));
      blockTag.click(e => {
        // If clicked inside child popup, ignore click
        if (!blockTag.is(e.target) && $(e.target).parentsUntil(blockTag).is(function() {return this.classList.contains('details-popup');})) {
          return;
        }
        // Find existing child popup, if any
        const existingPopup = $('.details-popup', blockTag);
        if (existingPopup.length > 0) {
          if (barBlockPopup !== undefined && existingPopup.is(barBlockPopup.popupTag)) {
            closePopup();
          }
          existingPopup.remove();
        } else {
          // Remove existing popup if there is one open
          closePopup();
          // Create new popup element
          const newPopup = createPopup(worldId, attrType, date, snapshotIds, blockTag, snapsUrlBase);
          // Add popup to the DOM and save the state
          openPopup(newPopup, blockTag, true);
        }
      });
      blockTag.removeAttr('all-snapshots');
      blockTag.removeAttr('day');
    });
  });
  
  $(window).click(event => {
    if (barBlockPopup === undefined) {
      return;
    }
    const popupDOM = barBlockPopup.popupTag[0];
    const parentDOM = barBlockPopup.parentTag[0];
    if (event.target !== popupDOM && event.target !== parentDOM && !$.contains(popupDOM, event.target) && !$.contains(parentDOM, event.target)) {
      closePopup();
    }
  });
  worldStates = worldStateData;
};
