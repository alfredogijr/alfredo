(function () {
  var WA = 'https://wa.me/5521971585367?text=';

  // Tones: the colour chart, each with its photograph and the suggested service
  var TONS = {
    dourado:   { nome: 'loiro dourado', servico: 'Mechas',           preco: true,  img: 'trabalho-02-loiro-dourado',            alt: 'Loiro dourado ondulado, atendido no salão' },
    bege:      { nome: 'bege',          servico: 'Mechas',           preco: true,  img: 'trabalho-05-morena-iluminada-bege',     alt: 'Iluminado em tom bege, atendido no salão' },
    mel:       { nome: 'mel',           servico: 'Morena iluminada', preco: true,  img: 'trabalho-01-morena-iluminada-mel',      alt: 'Morena iluminada com mechas mel, atendida no salão' },
    caramelo:  { nome: 'caramelo',      servico: 'Morena iluminada', preco: true,  img: 'trabalho-07-morena-iluminada-caramelo', alt: 'Morena iluminada em caramelo, atendida no salão', w: 900 },
    acobreado: { nome: 'acobreado',     servico: 'Morena iluminada', preco: true,  img: 'trabalho-04-morena-acobreada',          alt: 'Morena com pontas acobreadas, atendida no salão' },
    ruivo:     { nome: 'ruivo cobre',   servico: 'Ruivo',            preco: false, img: 'trabalho-08-ruivo-cobre',               alt: 'Ruivo cobre, atendido no salão' }
  };

  // Measure: every WhatsApp click is pushed with its origin, for GA4 / GTM and the Meta Pixel when present
  function track(origem, extra) {
    var data = Object.assign({ event: 'whatsapp_click', origem: origem }, extra || {});
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(data);
    if (typeof window.gtag === 'function') window.gtag('event', 'whatsapp_click', data);
    if (typeof window.fbq === 'function') window.fbq('track', 'Contact', data);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href*="wa.me"]');
    if (a) track(a.dataset.origem || 'outro', a.dataset.tom ? { tom: a.dataset.tom } : null);
  });

  // Choose your colour: the tone builds the result and a WhatsApp message that asks for a photo of the hair today
  var form = document.querySelector('.lab__steps');
  var result = document.querySelector('.lab__result');
  if (form && result) {
    var foto = result.querySelector('.lab__foto');
    var img = foto.querySelector('img');
    var servico = result.querySelector('.lab__servico');
    var preco = result.querySelector('.lab__preco');
    var cta = result.querySelector('.lab__cta');

    function update() {
      var key = (form.querySelector('input[name="tom"]:checked') || {}).value || 'mel';
      var t = TONS[key];
      foto.style.setProperty('--tone', 'var(--tone-' + key + ')');
      if (img.dataset.key !== key) {
        foto.classList.remove('is-in');
        void foto.offsetWidth;
        img.src = 'img/' + t.img + '.webp';
        img.srcset = 'img/' + t.img + '-600.webp 600w, img/' + t.img + '.webp ' + (t.w || 1200) + 'w';
        img.width = t.w || 1200;
        img.alt = t.alt;
        img.dataset.key = key;
        foto.classList.add('is-in');
      }
      servico.textContent = t.servico;
      preco.hidden = !t.preco;
      var msg = 'Olá! Escolhi o tom ' + t.nome + ' no site. Vou mandar uma foto do meu cabelo como está hoje para vocês avaliarem.';
      cta.href = WA + encodeURIComponent(msg);
      cta.dataset.tom = key;
    }
    form.addEventListener('change', update);
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    update();

    // A swatch in the hero picks its tone in the lab
    document.querySelectorAll('.mecha a[data-tom]').forEach(function (a) {
      a.addEventListener('click', function () {
        var r = document.getElementById('t-' + a.dataset.tom);
        if (r) { r.checked = true; update(); }
      });
    });
  }

  // Service rows preview their photograph beside the list
  var prev = document.querySelector('.preview');
  if (prev && window.matchMedia('(hover: hover) and (min-width: 60rem)').matches) {
    var layers = prev.querySelectorAll('img');
    var front = 0;
    function show(src) {
      if (!src || layers[front].getAttribute('src') === src) return;
      var back = 1 - front;
      layers[back].src = src;
      layers[back].classList.add('is-on');
      layers[front].classList.remove('is-on');
      front = back;
    }
    document.querySelectorAll('.servicos li[data-preview]').forEach(function (li) {
      li.addEventListener('mouseenter', function () { show(li.dataset.preview); });
      li.addEventListener('focusin', function () { show(li.dataset.preview); });
    });
  }

  // Lual: one pass of light across the word when it comes into view
  var word = document.querySelector('.lual__big');
  if (word && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { word.classList.add('is-lit'); io.disconnect(); } });
    }, { threshold: 0.6 });
    io.observe(word);
  }

  // Today in the opening hours
  var d = String(new Date().getDay());
  document.querySelectorAll('.horas tr').forEach(function (tr) {
    if (tr.dataset.dias.split(' ').indexOf(d) > -1) {
      tr.classList.add('is-hoje');
      tr.querySelector('th').insertAdjacentHTML('beforeend', ' <small>(hoje)</small>');
    }
  });
})();
