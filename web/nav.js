(function () {
  var menuBtn = document.getElementById('menuBtn');
  var drawer = document.getElementById('drawer');
  var overlay = document.getElementById('drawerOverlay');
  var closeBtn = document.getElementById('drawerClose');

  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add('is-open');
    if (overlay) overlay.classList.add('is-open');
    drawer.removeAttribute('aria-hidden');
  }
  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.remove('is-open');
    if (overlay) overlay.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
  }

  if (menuBtn) menuBtn.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', closeDrawer);

  // 現在ページのリンクをアクティブに
  var path = window.location.pathname.replace(/\/$/, '') || '/';
  document.querySelectorAll('.drawer-link[href]').forEach(function (link) {
    var href = link.getAttribute('href').replace(/\/$/, '') || '/';
    if (href === path) link.classList.add('drawer-link--active');
  });

  // ログイン状態取得
  fetch('/api/me', { credentials: 'same-origin' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (me) {
      var loggedIn = !!(me && me.user_id);
      var loginStatus = document.getElementById('loginStatus');
      var googleLogin = document.getElementById('googleLogin');
      var logoutBtn = document.getElementById('logoutBtn');
      var galleryBtn = document.getElementById('galleryBtn');
      var collectionBtn = document.getElementById('collectionBtn');

      if (loginStatus) loginStatus.textContent = loggedIn ? (me.email || 'ログイン中') : '';
      if (googleLogin) googleLogin.style.display = loggedIn ? 'none' : '';
      if (logoutBtn) logoutBtn.style.display = loggedIn ? '' : 'none';
      if (galleryBtn) galleryBtn.style.display = loggedIn ? '' : 'none';
      if (collectionBtn) collectionBtn.style.display = loggedIn ? '' : 'none';

      if (googleLogin) googleLogin.addEventListener('click', function () { location.href = '/login'; });
      if (logoutBtn) logoutBtn.addEventListener('click', function () {
        fetch('/logout', { method: 'POST', credentials: 'same-origin' })
          .then(function () { location.href = '/'; });
      });
    })
    .catch(function () {});

  // ===== 集めた魚種印モーダル（トップページ以外の共通実装）=====
  // トップページは app.js 側が同名のUIを持つのでこちらは動かない（nav.js を読まないため）。
  var CREATURE_DEX = [
    { key: 'has_jellyfish', name: 'クラゲ',     icon: '🪼' },
    { key: 'has_penguin',   name: 'ペンギン',   icon: '🐧' },
    { key: 'has_dolphin',   name: 'イルカ',     icon: '🐬' },
    { key: 'has_orca',      name: 'シャチ',     icon: '🐋' },
    { key: 'has_beluga',    name: 'シロイルカ', icon: '🐳' },
    { key: 'has_shark',     name: 'サメ',       icon: '🦈' },
    { key: 'has_sealion',   name: 'アシカ',     icon: '🦭' },
    { key: 'has_seal',      name: 'アザラシ',   icon: '🦭' },
    { key: 'has_steller',   name: 'トド',       icon: '🦭' },
  ];

  function navEsc(s) {
    return String(s).replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
  }

  // モーダルの箱が無いページでは作る（マークアップは index.html と同じ）
  function ensureCollectionModal() {
    var modal = document.getElementById('collectionModal');
    if (modal) return modal;
    modal = document.createElement('div');
    modal.id = 'collectionModal';
    modal.className = 'modal-overlay';
    modal.style.display = 'none';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.innerHTML =
      '<div class="modal-box collection-modal-box">' +
      '<p class="modal-title">🐟 集めた魚種印</p>' +
      '<div id="collectionSummary" class="collection-summary"></div>' +
      '<div id="collectionContent" class="collection-content"></div>' +
      '<div class="modal-actions">' +
      '<button id="collectionModalClose" class="modal-btn modal-btn--cancel">閉じる</button>' +
      '</div></div>';
    document.body.appendChild(modal);

    var closeIt = function () { modal.style.display = 'none'; };
    modal.querySelector('#collectionModalClose').addEventListener('click', closeIt);
    modal.addEventListener('click', function (e) { if (e.target === modal) closeIt(); });
    return modal;
  }

  function renderCollection(items) {
    var modal = ensureCollectionModal();
    var summary = document.getElementById('collectionSummary');
    var content = document.getElementById('collectionContent');

    var visited = (items || []).filter(function (x) { return x.visited; });

    if (summary) { summary.innerHTML = ''; summary.style.display = 'none'; }
    content.innerHTML = '';

    var grid = document.createElement('div');
    grid.className = 'collection-grid';
    var detail = document.createElement('div');
    detail.className = 'collection-detail';
    detail.hidden = true;

    CREATURE_DEX.forEach(function (c) {
      var aquariums = visited.filter(function (x) { return x[c.key]; })
                             .map(function (x) { return x.name; });
      var collected = aquariums.length > 0;

      var cell = document.createElement('div');
      cell.className = 'collection-cell' + (collected ? ' got' : ' locked');
      cell.innerHTML =
        '<div class="collection-icon">' + (collected ? c.icon : '❔') + '</div>' +
        '<div class="collection-name">' + navEsc(c.name) + '</div>' +
        '<div class="collection-count">' + (collected ? '×' + aquariums.length + '館' : '未ゲット') + '</div>';
      if (collected) {
        cell.onclick = function () {
          detail.hidden = false;
          detail.innerHTML =
            '<div class="collection-detail-title">' + c.icon + ' ' + navEsc(c.name) +
            ' に会えた水族館（' + aquariums.length + '）</div>' +
            '<div class="collection-detail-list">' + aquariums.map(navEsc).join(' / ') + '</div>';
        };
      }
      grid.appendChild(cell);
    });

    content.appendChild(grid);
    content.appendChild(detail);
    modal.style.display = '';
  }

  var navItemsCache = null;
  var navCollectionBtn = document.getElementById('collectionBtn');
  if (navCollectionBtn) {
    navCollectionBtn.addEventListener('click', function () {
      closeDrawer();
      if (navItemsCache) { renderCollection(navItemsCache); return; }
      var modal = ensureCollectionModal();
      document.getElementById('collectionContent').innerHTML =
        '<div style="padding:24px;text-align:center;color:#888;">読み込み中...</div>';
      modal.style.display = '';
      fetch('/api/aquariums', { credentials: 'same-origin' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (items) {
          if (!items) throw new Error('failed');
          navItemsCache = items;
          renderCollection(items);
        })
        .catch(function () {
          document.getElementById('collectionContent').innerHTML =
            '<div style="padding:24px;text-align:center;color:#888;">読み込みに失敗しました</div>';
        });
    });
  }

  // お知らせベル（ヘッダーの更新情報ポップアップ）
  var bellBtn = document.getElementById('updateBellBtn');
  var bellBadge = document.getElementById('bellBadge');
  var bellPop = document.getElementById('bellPopover');
  if (bellBtn && bellBadge && bellPop) {
    var bellDateEl = bellPop.querySelector('.bell-popover__date');
    var bellLatest = bellDateEl ? bellDateEl.textContent.trim() : '';
    var BELL_SEEN_KEY = 'aq_lastSeenUpdate';
    var bellLastSeen = localStorage.getItem(BELL_SEEN_KEY) || '';

    if (bellLatest && bellLatest > bellLastSeen) {
      bellBadge.hidden = false;
      bellBtn.classList.add('is-shaking');
    }

    var closeBellPopover = function () {
      bellPop.hidden = true;
      bellBtn.setAttribute('aria-expanded', 'false');
    };
    var openBellPopover = function () {
      bellPop.hidden = false;
      bellBtn.setAttribute('aria-expanded', 'true');
      bellBadge.hidden = true;
      bellBtn.classList.remove('is-shaking');
      if (bellLatest) localStorage.setItem(BELL_SEEN_KEY, bellLatest);
    };

    bellBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (bellPop.hidden) openBellPopover(); else closeBellPopover();
    });
    document.addEventListener('click', function (e) {
      if (!bellPop.hidden && !bellPop.contains(e.target) && e.target !== bellBtn) closeBellPopover();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeBellPopover();
    });
  }
})();
