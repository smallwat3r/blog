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
