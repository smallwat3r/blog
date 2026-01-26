document.querySelectorAll('pre').forEach((pre) => {
  const wrapper = document.createElement('div');
  wrapper.className = 'pre-wrapper';
  pre.parentNode.insertBefore(wrapper, pre);
  wrapper.appendChild(pre);

  const btn = document.createElement('span');
  btn.className = 'copy-btn';
  btn.textContent = 'copy';
  wrapper.appendChild(btn);

  wrapper.addEventListener('click', () => {
    navigator.clipboard?.writeText(pre.textContent).then(() => {
      btn.textContent = 'copied!';
      setTimeout(() => { btn.textContent = 'copy'; }, 1500);
    });
  });
});

// Heading anchor links
document.querySelectorAll('article h2[id], article h3[id]').forEach((h) => {
  const link = document.createElement('a');
  link.href = '#' + h.id;
  link.className = 'heading-link';
  link.innerHTML = h.innerHTML;
  h.textContent = '';
  h.appendChild(link);

  const pilcrow = document.createElement('span');
  pilcrow.className = 'pilcrow';
  pilcrow.textContent = '\u00B6';
  link.prepend(pilcrow);
});

// Table of contents
(function() {
  const toc = document.querySelector('.toc');
  const headings = document.querySelectorAll('article h2[id], article h3[id]');
  if (!toc || headings.length < 2) return;

  const title = document.createElement('div');
  title.className = 'toc-title';
  title.textContent = 'Contents';
  toc.appendChild(title);

  const ul = document.createElement('ul');
  const links = [];
  let currentSubUl = null;

  headings.forEach((h) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#' + h.id;
    // Get text without the pilcrow
    const clone = h.cloneNode(true);
    const pilcrow = clone.querySelector('.pilcrow');
    if (pilcrow) pilcrow.remove();
    a.textContent = clone.textContent;
    li.appendChild(a);

    if (h.tagName === 'H2') {
      ul.appendChild(li);
      currentSubUl = null;
    } else {
      li.className = 'toc-sub';
      if (!currentSubUl) {
        currentSubUl = document.createElement('ul');
        currentSubUl.className = 'toc-sublist';
        ul.appendChild(currentSubUl);
      }
      currentSubUl.appendChild(li);
    }
    links.push({ el: a, target: h });
  });
  toc.appendChild(ul);

  // Highlight current section on scroll
  let ticking = false;
  function updateActive() {
    const scrollY = window.scrollY + 100;
    let current = links[0];
    for (const link of links) {
      if (link.target.offsetTop <= scrollY) current = link;
    }
    links.forEach((l) => l.el.classList.toggle('active', l === current));
  }
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => { updateActive(); ticking = false; });
      ticking = true;
    }
  });
  updateActive();
})();
