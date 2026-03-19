'use strict';

// Load locales JSON synchronously and expose as window.lang
// Params (via script src query): base, loc, cache
(function () {
  try {
    const src = document.currentScript && document.currentScript.src || '';
    const qIndex = src.indexOf('?');
    const params = {};

    if (qIndex !== -1) {
      const query = src.substring(qIndex + 1);

      query.split('&').forEach(pair => {
        const kv = pair.split('=');

        if (kv.length === 2) params[decodeURIComponent(kv[0])] = decodeURIComponent(kv[1]);
      });
    }

    const base = params.base || '';
    const loc = params.loc || 'en';
    const cache = params.cache || String(Date.now());

    const jsonUrl = `${base + loc}.json?cache=${cache}`;
    const xhr = new XMLHttpRequest();

    try {
      xhr.open('GET', jsonUrl, false); // sync to ensure window.lang present before app.js
      xhr.send(null);
      if (xhr.status >= 200 && xhr.status < 300 && xhr.responseText) {
        window.lang = JSON.parse(xhr.responseText);
      } else {
        // eslint-disable-next-line no-console
        console.error('[locales][app] JSON load failed', jsonUrl, xhr.status);
        window.lang = {};
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('[locales][app] JSON load error', jsonUrl, e && e.message ? e.message : e);
      window.lang = {};
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[locales][app] loader init error', err && err.message ? err.message : err);
    if (!window.lang) window.lang = {};
  }
}());
