(() => {
  const body = document.body;
  const themeButton = document.querySelector('[data-theme-toggle]');
  const savedTheme = (() => { try { return localStorage.getItem('parking-theme'); } catch (_) { return null; } })();
  if (savedTheme === 'light') body.classList.remove('dark'); else body.classList.add('dark');
  function updateThemeIcon() {
    if (!themeButton) return;
    themeButton.innerHTML = body.classList.contains('dark')
      ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20.9 13A8.5 8.5 0 0 1 11 3.1 8.5 8.5 0 1 0 20.9 13Z"/></svg>';
    themeButton.setAttribute('aria-label', body.classList.contains('dark') ? 'Switch to light theme' : 'Switch to dark theme');
  }
  updateThemeIcon();
  themeButton?.addEventListener('click', () => {
    body.classList.toggle('dark');
    try { localStorage.setItem('parking-theme', body.classList.contains('dark') ? 'dark' : 'light'); } catch (_) {}
    updateThemeIcon();
  });

  const search = document.querySelector('[data-slot-search]');
  const filter = document.querySelector('[data-slot-filter]');
  const cards = [...document.querySelectorAll('[data-slot-card]')];
  const visibleCount = document.querySelector('[data-visible-count]');
  function applyFilters() {
    const q = (search?.value || '').trim().toLowerCase();
    const status = filter?.value || 'all';
    let visible = 0;
    cards.forEach(card => {
      const matchText = (card.dataset.search || '').toLowerCase().includes(q);
      const matchStatus = status === 'all' || card.dataset.status === status;
      const show = matchText && matchStatus;
      card.hidden = !show;
      if (show) visible++;
    });
    if (visibleCount) visibleCount.textContent = `${visible} shown`;
  }
  search?.addEventListener('input', applyFilters);
  filter?.addEventListener('change', applyFilters);

  document.querySelectorAll('[data-reserve-trigger]').forEach(button => {
    button.addEventListener('click', () => {
      const form = document.querySelector(`#reserve-form-${button.dataset.reserveTrigger}`);
      if (form) {
        form.hidden = !form.hidden;
        if (!form.hidden) form.querySelector('input')?.focus();
        button.setAttribute('aria-expanded', String(!form.hidden));
      }
    });
  });

  document.querySelectorAll('[data-confirm-release]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm('Release this parking slot and clear its vehicle details?')) event.preventDefault();
    });
  });
  document.querySelectorAll('[data-flash]').forEach(message => {
    window.setTimeout(() => { message.style.opacity = '0'; message.style.transform = 'translateY(-4px)'; }, 4800);
    window.setTimeout(() => message.remove(), 5200);
  });
  const clock = document.querySelector('[data-live-clock]');
  if (clock) {
    const renderClock = () => { clock.textContent = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date()); };
    renderClock(); window.setInterval(renderClock, 30000);
  }
})();
