(() => {
  const body = document.body;
  const toggle = document.querySelector("[data-menu-toggle]");
  const flashes = document.querySelectorAll("[data-flash-close]");
  const skillFilter = document.querySelector("[data-skill-filter]");
  const skillOptions = document.querySelectorAll(".skill-options label");

  if (toggle) {
    toggle.addEventListener("click", () => {
      const open = body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  flashes.forEach((btn) => {
    btn.addEventListener("click", () => btn.closest(".flash-item")?.remove());
  });

  if (skillFilter && skillOptions.length) {
    skillFilter.addEventListener("input", () => {
      const q = skillFilter.value.trim().toLowerCase();
      skillOptions.forEach((label) => {
        const text = label.textContent.toLowerCase();
        label.hidden = q.length > 0 && !text.includes(q);
      });
    });
  }

  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (event) => {
      const message = el.getAttribute("data-confirm");
      if (message && !window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  const filterForm = document.querySelector("[data-filter-form]");
  if (filterForm) {
    filterForm.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", () => filterForm.requestSubmit());
    });
  }
})();
