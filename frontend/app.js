/* Trading-AI - Minimal interactive JavaScript (app.js)
   Enhances accessibility and provides lightweight interactivity for the static HTML.
   - Sets current year
   - Handles contact form submission (local placeholder)
   - Updates live market status placeholders with simulated values
   - Adds simple nav link active state on scroll
*/

(function(){
  'use strict';

  // Utility: safe query
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  document.addEventListener('DOMContentLoaded', () => {
    // Set dynamic year in footer
    const y = new Date().getFullYear();
    const yearEl = document.getElementById('copyright-year');
    if(yearEl) yearEl.textContent = String(y);

    // Contact form handler (placeholder)
    const form = document.getElementById('contact-form');
    if(form){
      form.addEventListener('submit', (ev) => {
        ev.preventDefault();
        // Basic validation
        const name = $('#contact-name').value.trim();
        const email = $('#contact-email').value.trim();
        const message = $('#contact-message').value.trim();
        if(!name || !email || !message){
          alert('Please complete all required fields.');
          return;
        }
        // Simulate async submit
        const submitBtn = $('#contact-submit');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Submit';
          alert('Thank you, your message has been submitted (demo).');
          form.reset();
        }, 900);
      });
    }

    // Live market status simulation (updates placeholders)
    const statusPlaceholders = $$('.status-placeholder');
    if(statusPlaceholders.length){
      // small utility to format ms
      const fmtLatency = (ms) => `${Math.round(ms)} ms`;
      const exchanges = ['OK', 'DEGRADED', 'OFFLINE'];
      setInterval(() => {
        statusPlaceholders.forEach((el, idx) => {
          if(idx === 0){
            // exchange connectivity rotate
            el.textContent = exchanges[Math.floor(Math.random()*exchanges.length)];
          } else if(idx === 1){
            el.textContent = new Date().toLocaleTimeString();
          } else if(idx === 2){
            el.textContent = fmtLatency(Math.random()*300);
          }
        });
      }, 2000);
    }

    // Simple scrollspy to highlight active nav link
    const navLinks = $$('.primary-navigation .nav-link');
    const sections = navLinks.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
    const markActive = () =>{
      const scrollY = window.scrollY + 120; // offset for header
      let activeId = null;
      sections.forEach(sec =>{
        if(sec.offsetTop <= scrollY) activeId = sec.id;
      });
      navLinks.forEach(a =>{
        const target = a.getAttribute('href').slice(1);
        if(target === activeId) a.classList.add('active'); else a.classList.remove('active');
      });
    };
    if(sections.length) {
      markActive();
      window.addEventListener('scroll', throttle(markActive, 150));
    }

    // CTA demo: scroll to demo section
    const demoBtn = document.getElementById('cta-view-demo');
    if(demoBtn){
      demoBtn.addEventListener('click', (ev)=>{
        ev.preventDefault();
        const target = document.getElementById('market-overview');
        if(target) target.scrollIntoView({behavior:'smooth',block:'start'});
      });
    }

    // Login/Signup placeholder handlers
    const loginBtn = document.getElementById('login-button');
    const signupBtn = document.getElementById('signup-button');
    if(loginBtn) loginBtn.addEventListener('click', ()=> alert('Login flow placeholder.'));
    if(signupBtn) signupBtn.addEventListener('click', ()=> alert('Signup flow placeholder.'));

  });

  // Simple throttle
  function throttle(fn, wait){
    let last = 0; let timer = null;
    return function(...args){
      const now = Date.now();
      const remaining = wait - (now - last);
      if(remaining <= 0){
        if(timer){ clearTimeout(timer); timer = null; }
        last = now; fn.apply(this, args);
      } else if(!timer){
        timer = setTimeout(()=>{ last = Date.now(); timer = null; fn.apply(this, args); }, remaining);
      }
    };
  }

})();
