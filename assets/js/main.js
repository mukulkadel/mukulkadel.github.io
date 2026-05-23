/* eslint-disable */
(function () {
  'use strict';

  // ── Mermaid: convert fenced code blocks to render targets ──────────────────
  function initMermaid() {
    if (typeof mermaid === 'undefined') return;

    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    mermaid.initialize({
      startOnLoad: false,
      theme: isDark ? 'dark' : 'default',
      securityLevel: 'loose',
      fontFamily: 'inherit',
    });

    const codeBlocks = document.querySelectorAll('code.language-mermaid');
    codeBlocks.forEach(function (code) {
      const pre = code.parentElement;
      if (!pre) return;
      const container = document.createElement('div');
      container.className = 'mermaid';
      container.textContent = code.textContent;
      pre.replaceWith(container);
    });

    mermaid.run({ querySelector: '.mermaid' });
  }

  // ── highlight.js: syntax-highlight all code blocks ────────────────────────
  function initHighlight() {
    if (typeof hljs === 'undefined') return;
    document.querySelectorAll('pre code:not(.language-mermaid)').forEach(function (block) {
      hljs.highlightElement(block);
    });
  }

  // ── Add language label to pre blocks ──────────────────────────────────────
  function addCodeLabels() {
    document.querySelectorAll('pre code').forEach(function (code) {
      const pre = code.parentElement;
      const classes = Array.from(code.classList);
      const langClass = classes.find(function (c) { return c.startsWith('language-'); });
      if (langClass) {
        const lang = langClass.replace('language-', '');
        if (lang && lang !== 'plaintext' && lang !== 'text') {
          pre.setAttribute('data-lang', lang);
        }
      }
    });
  }

  // ── Copy-to-clipboard button for code blocks ──────────────────────────────
  function addCopyButtons() {
    document.querySelectorAll('pre').forEach(function (pre) {
      if (pre.querySelector('.copy-btn')) return;

      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.setAttribute('aria-label', 'Copy code');
      btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';

      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        if (!code) return;
        navigator.clipboard.writeText(code.textContent).then(function () {
          btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
          setTimeout(function () {
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
          }, 2000);
        });
      });

      pre.style.position = 'relative';
      pre.appendChild(btn);
    });
  }

  // ── Share: copy link button ───────────────────────────────────────────────
  function initShareCopyButton() {
    var btn = document.querySelector('.share-btn--copy');
    if (!btn) return;
    var url = btn.getAttribute('data-url');
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(url).then(function () {
        var label = btn.querySelector('.share-btn-label');
        label.textContent = 'Copied!';
        setTimeout(function () { label.textContent = 'Copy link'; }, 2000);
      });
    });
  }

  // ── Reading progress bar ──────────────────────────────────────────────────
  function initReadingProgress() {
    var bar = document.querySelector('.reading-progress');
    if (!bar) return;
    window.addEventListener('scroll', function () {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = Math.min(pct, 100) + '%';
    }, { passive: true });
  }

  // ── Mobile nav toggle ──────────────────────────────────────────────────────
  function initNavToggle() {
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.querySelector('.site-nav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ── Boot ──────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    addCodeLabels();
    initMermaid();
    initHighlight();
    addCopyButtons();
    initShareCopyButton();
    initReadingProgress();
    initNavToggle();
  });
})();
