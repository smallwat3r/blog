document.addEventListener("DOMContentLoaded", () => {
  const filter = document.querySelector(".tags-filter");
  const items = [...document.querySelectorAll("ul li[data-tags]")]
    .map((li) => ({
      el: li,
      tags: new Set(li.dataset.tags.split(",")),
    }));
  const active = new Set();

  const update = () => {
    for (const { el, tags } of items) {
      if (active.size === 0) {
        el.style.display = "";
        continue;
      }
      const match = [...active].some((t) => tags.has(t));
      el.style.display = match ? "" : "none";
    }
  };

  filter.addEventListener("click", (e) => {
    const btn = e.target.closest(".tag-btn");
    if (!btn) return;
    const tag = btn.dataset.tag;
    if (active.has(tag)) {
      active.delete(tag);
    } else {
      active.add(tag);
    }
    btn.classList.toggle("active");
    btn.blur();
    update();
  });
});
