document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector(".project-search");
  const items = [...document.querySelectorAll(".project-item")]
    .map((el) => ({
      el,
      text: (el.dataset.search || "").toLowerCase(),
    }));

  input.addEventListener("input", () => {
    const q = input.value.toLowerCase().trim();
    for (const { el, text } of items) {
      el.style.display = !q || text.includes(q) ? "" : "none";
    }
  });
});
