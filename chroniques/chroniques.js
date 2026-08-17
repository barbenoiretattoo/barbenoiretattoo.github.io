/* ═══════════════════════════════════════════════════════
   BARBE NOIRE TATTOO — Chroniques : comportements partagés
   Chargé par chroniques/index.html et par chaque chroniques/<slug>/index.html
   (noms de fichiers/classes internes conservés en « blog » par simplicité)
   ═══════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  const yearEl = document.getElementById('year');
  if(yearEl) yearEl.textContent = new Date().getFullYear();

  /* nav au défilement + bouton remonter */
  const nav = document.getElementById('nav');
  const toTop = document.getElementById('toTop');
  let ticking = false;
  window.addEventListener('scroll', () => {
    if(ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      if(nav) nav.classList.toggle('scrolled', y > 40);
      if(toTop) toTop.classList.toggle('show', y > 700);
      ticking = false;
    });
  }, {passive:true});
  if(toTop) toTop.addEventListener('click', () => window.scrollTo({top:0,behavior:'smooth'}));

  /* menu mobile */
  const burger = document.getElementById('burger');
  const navLinks = document.getElementById('navLinks');
  if(burger && navLinks){
    burger.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      burger.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      navLinks.classList.remove('open');
      burger.classList.remove('open');
      burger.setAttribute('aria-expanded','false');
      document.body.style.overflow = '';
    }));
  }

  /* apparition au scroll */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if(e.isIntersecting){ e.target.classList.add('visible'); io.unobserve(e.target); } });
  }, {threshold:.1});
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  /* Filet de sécurité : un saut de défilement rapide (clic dans le menu,
     lien direct, retour navigateur...) peut faire passer un bloc dans
     l'écran sans que l'observateur ne le détecte, le laissant invisible
     en permanence. On revérifie donc régulièrement. */
  function catchUpRevealsNow(){
    document.querySelectorAll('.reveal:not(.visible)').forEach(el => {
      if(el.getBoundingClientRect().top < window.innerHeight){
        el.classList.add('visible');
        io.unobserve(el);
      }
    });
  }
  window.addEventListener('scroll', catchUpRevealsNow, {passive:true});
  window.addEventListener('load', catchUpRevealsNow);
  window.addEventListener('hashchange', catchUpRevealsNow);
  if(navLinks) navLinks.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', () => setTimeout(catchUpRevealsNow, 450)));
  catchUpRevealsNow();
  /* vérification périodique en secours, tant qu'il reste des blocs non révélés */
  const revealSafetyNet = setInterval(() => {
    if(document.querySelectorAll('.reveal:not(.visible)').length === 0){
      clearInterval(revealSafetyNet);
      return;
    }
    catchUpRevealsNow();
  }, 400);

  /* lightbox sur les images marquées .plaque[data-full] */
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxClose = document.getElementById('lightboxClose');
  function openLightbox(src, alt){
    if(!lightbox || !lightboxImg) return;
    lightboxImg.src = src;
    if(alt) lightboxImg.alt = alt;
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeLightbox(){
    if(!lightbox) return;
    lightbox.classList.remove('open');
    lightboxImg.src = '';
    document.body.style.overflow = '';
  }
  if(lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
  if(lightbox) lightbox.addEventListener('click', e => { if(e.target === lightbox) closeLightbox(); });

  /* modale mentions légales */
  function openModal(id){ const m = document.getElementById(id); if(m){ m.classList.add('open'); document.body.style.overflow='hidden'; } }
  function closeModal(id){ const m = document.getElementById(id); if(m){ m.classList.remove('open'); document.body.style.overflow=''; } }
  const openLegalBtn = document.getElementById('openLegal');
  if(openLegalBtn) openLegalBtn.addEventListener('click', () => openModal('legalModal'));
  document.querySelectorAll('.modal-close').forEach(btn => btn.addEventListener('click', () => closeModal(btn.dataset.close)));
  document.querySelectorAll('.modal').forEach(m => m.addEventListener('click', e => { if(e.target === m) closeModal(m.id); }));

  document.addEventListener('keydown', e => {
    if(e.key === 'Escape'){
      closeLightbox();
      document.querySelectorAll('.modal.open').forEach(m => closeModal(m.id));
    }
  });
  document.querySelectorAll('.plaque[data-full]').forEach(el => {
    el.style.cursor = 'zoom-in';
    el.addEventListener('click', () => {
      const img = el.querySelector('img');
      openLightbox(el.dataset.full, img ? img.alt : '');
    });
  });
});
