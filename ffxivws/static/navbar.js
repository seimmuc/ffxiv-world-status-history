let openMenus = undefined;

function navbarMenusOpen(toOpen) {
  const toClose = new Set(openMenus);
  openMenus = [];
  toOpen.forEach(e => {
    toClose.delete(e);
    e.classList.add('open');
    openMenus.push(e);
  });
  toClose.forEach(e => {
    e.classList.remove('open');
  });
  if (openMenus.length < 1) {
    openMenus = undefined;
  }
}

function navbarMenuGetSubmenuButton(elem) {
  const elemTag = $(elem);
  if (elemTag.hasClass('navmenu')) {
    return undefined;
  }
  const beforeNM = elemTag.parentsUntil('.navmenu').add(elemTag);
  if (beforeNM.hasClass('dropdown') || beforeNM.hasClass('dropright')) {
    return beforeNM.filter('.dropdown, .dropright')[0];
  }
  return undefined;
}

$(document).ready(function() {
  if (!window.matchMedia( "(hover: none)" ).matches) {
    return;
  }
  $('#navbar li.dropdown, #navbar li.dropright').each(function() {
    const listItem = $(this);
    const linkTag = $('a', listItem);
    const childMenu = $('.navmenu', listItem).first();
    const parentMenus = listItem.parentsUntil('#navbar', '.navmenu:not(.root)');
    listItem.on('touchstart', e => {
      if (navbarMenuGetSubmenuButton(e.target) !== listItem[0]) {
        return;
      }
      let toOpen;
      if (openMenus !== undefined && openMenus.includes(childMenu[0])) {
        toOpen = parentMenus.toArray();
      } else {
        toOpen = parentMenus.add(childMenu).toArray();
      }
      navbarMenusOpen(toOpen);
    });
  });
  $(window).on('touchstart', e => {
    if (openMenus === undefined) {
      return;
    }
    if ($(e.target).parents('#navbar').length > 0) {
      if (navbarMenuGetSubmenuButton(e.target)) {
        return;
      }
      const targetTag = $(e.target);
      const keepOpen = targetTag.parentsUntil('#navbar', '.navmenu:not(.root)').add(targetTag).toArray();
      navbarMenusOpen(keepOpen);
    } else {
      openMenus.forEach(e => e.classList.remove('open'));
      openMenus = undefined;
    }
  });
});
