document.addEventListener('DOMContentLoaded', () => {
  const script1 = document.createElement('script');

  script1.src = 'https://apis.google.com/js/client.js';
  script1.async = true;
  document.head.appendChild(script1);

  const script2 = document.createElement('script');

  script2.src = 'https://www.youtube.com/iframe_api';
  script2.async = true;
  document.head.appendChild(script2);
});
