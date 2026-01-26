(function() {
  // Copy button for code blocks
  document.querySelectorAll('.pre-wrapper').forEach((wrapper) => {
    wrapper.addEventListener('click', () => {
      navigator.clipboard?.writeText(wrapper.querySelector('pre').textContent).then(() => {
        const btn = wrapper.querySelector('.copy-btn');
        btn.textContent = 'copied!';
        setTimeout(() => btn.textContent = 'copy', 1500);
      });
    });
  });

  // TOC highlighting
  const toc = document.querySelector('.toc');
  const article = document.querySelector('article');
  if (!toc || !article) return;

  const links = [...toc.querySelectorAll('a[href^="#"]')]
    .map((el) => ({ el, target: document.getElementById(el.hash.slice(1)) }))
    .filter((link) => link.target);
  if (links.length < 2) return;

  let hovered = null;
  let ticking = false;

  const highlight = (current) => {
    links.forEach((link) => link.el.classList.toggle('active', link === current));
  };

  const highlightByScroll = () => {
    if (hovered) return;
    const y = scrollY + 100;
    let current = links[0];
    for (const link of links) {
      if (link.target.offsetTop <= y) current = link;
    }
    highlight(current);
  };

  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { highlightByScroll(); ticking = false; });
  });

  article.addEventListener('mouseover', (e) => {
    const section = e.target.closest('section[id]');
    if (!section) return;
    hovered = links.find((link) => link.target.id === section.id);
    if (hovered) highlight(hovered);
  });

  article.addEventListener('mouseleave', () => {
    hovered = null;
    highlightByScroll();
  });

  highlightByScroll();
})();
