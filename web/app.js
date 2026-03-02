const $ = (id) => document.getElementById(id);

let state = {
  items: [],
  filter: "all",
  pref: "",
  sort: "pref_plain",
  lastMapKey: "",
  regionOpen: {},
};
state.loggedIn = false;
const PREF_ORDER = [
  "北海道",
  "青森県","岩手県","宮城県","秋田県","山形県","福島県",
  "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
  "新潟県","富山県","石川県","福井県","山梨県","長野県",
  "岐阜県","静岡県","愛知県","三重県",
  "滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
  "鳥取県","島根県","岡山県","広島県","山口県",
  "徳島県","香川県","愛媛県","高知県",
  "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県",
  "沖縄県"
];

const REGION_ORDER = ["北海道","東北","関東","中部","近畿","中国","四国","九州・沖縄"];

const REGION_BY_PREF = {
  "北海道": "北海道",
  "青森県":"東北","岩手県":"東北","宮城県":"東北","秋田県":"東北","山形県":"東北","福島県":"東北",
  "茨城県":"関東","栃木県":"関東","群馬県":"関東","埼玉県":"関東","千葉県":"関東","東京都":"関東","神奈川県":"関東",
  "新潟県":"中部","富山県":"中部","石川県":"中部","福井県":"中部","山梨県":"中部","長野県":"中部","岐阜県":"中部","静岡県":"中部","愛知県":"中部",
  "三重県":"近畿","滋賀県":"近畿","京都府":"近畿","大阪府":"近畿","兵庫県":"近畿","奈良県":"近畿","和歌山県":"近畿",
  "鳥取県":"中国","島根県":"中国","岡山県":"中国","広島県":"中国","山口県":"中国",
  "徳島県":"四国","香川県":"四国","愛媛県":"四国","高知県":"四国",
  "福岡県":"九州・沖縄","佐賀県":"九州・沖縄","長崎県":"九州・沖縄","熊本県":"九州・沖縄","大分県":"九州・沖縄","宮崎県":"九州・沖縄","鹿児島県":"九州・沖縄","沖縄県":"九州・沖縄",
};

function regionOf(pref) {
  return REGION_BY_PREF[pref] || "その他";
}



let map;
let markersLayer;




async function apiGet(path) {
  const res = await fetch(path, { credentials: "same-origin" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(path, {
    method: "PUT",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": state.csrfToken || "",
    },
    body: JSON.stringify(body),
  });

  const text = await res.text(); // 先に本文を読む

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${text || "(empty)"}`);
  }

  // 空レスポ(204など)でも落ちないように
  if (!text) return null;

  // JSONじゃない場合もあるのでtry
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

const CHANGELOG = [
  {
    date: "2026-03-02",
    items: [
      "ログイン導線（検索上のログイン案内）を追加",
      "写真追加ボタン：未ログイン時はログイン画面へ案内",
      "並び替え：都道府県順（デフォルト）/ 地域別 / 五十音順 を整理",
    ],
  },
  {
    date: "2026-03-01",
    items: [
      "訪問済ボタンの反応を改善（押した瞬間に見た目が変わる）",
      "写真表示の安定性を改善（必要な時だけ読み込み）",
    ],
  },
];

function renderTimeline() {
  const section = document.getElementById("timeline");
  const list = document.getElementById("timelineList");
  if (!section || !list) return;

  if (!CHANGELOG.length) {
    section.style.display = "none";
    return;
  }

  section.style.display = "";
  list.innerHTML = "";

  for (const entry of CHANGELOG) {
    const item = document.createElement("div");
    item.className = "timeline__item";

    const d = document.createElement("div");
    d.className = "timeline__date";
    d.textContent = entry.date;

    const body = document.createElement("div");
    body.className = "timeline__body";

    const ul = document.createElement("ul");
    for (const t of entry.items) {
      const li = document.createElement("li");
      li.textContent = t;
      ul.appendChild(li);
    }
    body.appendChild(ul);

    item.appendChild(d);
    item.appendChild(body);
    list.appendChild(item);
  }
}


function match(item, q) {
  if (!q) return true;
  const t = (item.name + " " + item.prefecture + " " + item.city + " " + item.location_raw).toLowerCase();
  return t.includes(q.toLowerCase());
}

function passesFilter(item) {
  // ★追加：都道府県
// 都道府県順のときだけ都道府県フィルタを効かせる
  if (state.sort === "pref" && state.pref && item.prefecture !== state.pref) return false;
  if (state.filter === "all") return true;
  if (state.filter === "visited") return item.visited;
  if (state.filter === "unvisited") return !item.visited;
  if (state.filter === "star") return item.mola_star === 1;
  return true;
}


function setPrefOptions(items) {
  const sel = $("pref-filter");
  if (!sel) return; // HTML側に無い場合は何もしない

  const current = sel.value || state.pref || "";
  const prefs = Array.from(
    new Set(items.map((x) => x.prefecture).filter(Boolean))
  ).sort((a, b) => a.localeCompare(b, "ja"));

  // option を作り直し
  sel.innerHTML = `<option value="">都道府県（すべて）</option>`;
  for (const p of prefs) {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    sel.appendChild(opt);
  }

  // できるだけ選択状態を維持
  sel.value = prefs.includes(current) ? current : "";
  state.pref = sel.value;
}

function showConfirm(title, body) {
  return new Promise((resolve) => {
    const overlay = document.getElementById("confirmModal");
    document.getElementById("confirmTitle").textContent = title;
    document.getElementById("confirmBody").textContent = body;
    overlay.style.display = "flex";

    function cleanup(result) {
      overlay.style.display = "none";
      document.getElementById("confirmOk").onclick = null;
      document.getElementById("confirmCancel").onclick = null;
      resolve(result);
    }

    document.getElementById("confirmOk").onclick = () => cleanup(true);
    document.getElementById("confirmCancel").onclick = () => cleanup(false);
  });
}

function renderCard(it) {
  const card = document.createElement("div");
  card.id = "card-" + it.id;
  card.className = "card" + (it.visited ? " is-visited" : "");

  // ★スタンプ風バッジ（訪問済み）
  if (it.visited) {
    const stamp = document.createElement("div");
    stamp.className = "stamp";
    stamp.textContent = "VISITED";
    card.appendChild(stamp);
  }

  let title;

  if (it.url) {
    title = document.createElement("a");
    title.href = it.url;
    title.target = "_blank";
    title.rel = "noopener noreferrer";
    title.className = "title link-title";
    title.textContent = it.name;
  } else {
    title = document.createElement("div");
    title.className = "title";
    title.textContent = it.name;
  }
  
  card.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = `${it.prefecture}${it.city ? " / " + it.city : ""} ${it.location_raw ? " / " + it.location_raw : ""}`;
  card.appendChild(meta);

  const row = document.createElement("div");
  row.className = "row2";

  const btn = document.createElement("button");
  btn.className = it.visited ? "btn visited" : "btn";
  btn.textContent = it.visited ? "訪問済✅（解除）" : "訪問済にする";

  // 訪問日入力・訪問回数表示（クロージャで参照するため先に宣言）
  const dateRow = document.createElement("div");
  const dateInput = document.createElement("input");
  let countDisplay = null; // ログイン中のみ後でセット

  if (!state.loggedIn) {
    btn.disabled = true;
    // ★追加：連打ガード（1秒以内の再クリックは捨てる）
const now = Date.now();
if (btn.dataset.lastClick && now - Number(btn.dataset.lastClick) < 1000) {
  btn.disabled = false;
  return;
}
btn.dataset.lastClick = String(now);
    btn.title = "ログインすると押せます";
  } else {
    btn.onclick = async () => {
      // ★最初に無効化（連打・二重タップ防止）
      if (btn.disabled) return;
      btn.disabled = true;

      // 解除時は確認ポップアップ
      if (it.visited && !(await showConfirm("訪問済を解除しますか？", "訪問日や訪問回数がリセットされます"))) {
        btn.disabled = false;
        return;
      }

      const newVisited = !it.visited;
    
      // ① 先にUIを即変更
      it.visited = newVisited;
      card.classList.toggle("is-visited", newVisited);
      btn.className = newVisited ? "btn visited" : "btn";
      btn.textContent = newVisited ? "訪問済✅（解除）" : "訪問済にする";
    
      // ② VISITEDバッジ（stamp）も即同期
      let stampEl = card.querySelector(".stamp");
      if (newVisited) {
        if (!stampEl) {
          stampEl = document.createElement("div");
          stampEl.className = "stamp";
          stampEl.textContent = "VISITED";
          card.appendChild(stampEl);
        }
      } else {
        if (stampEl) stampEl.remove();
      }
    
      // ③ 訪問日行の表示切替（楽観的）
      dateRow.style.display = newVisited ? "" : "none";
      if (newVisited && !dateInput.value) {
        const d = new Date();
        dateInput.value = d.getFullYear() + "-"
          + String(d.getMonth() + 1).padStart(2, "0") + "-"
          + String(d.getDate()).padStart(2, "0");
      }

      // ④ 訪問回数の楽観的更新（訪問済みにした時は最低1）
      const oldCount = it.visit_count || 0;
      if (newVisited && oldCount === 0) {
        it.visit_count = 1;
        if (countDisplay) countDisplay.textContent = "1";
      } else if (!newVisited) {
        it.visit_count = 0;
        if (countDisplay) countDisplay.textContent = "0";
      }

      try {
        const res = await apiPut(`/api/aquariums/${it.id}/visited`, { visited: newVisited });
        if (res && res.visited_at) {
          it.visited_at = res.visited_at;
          dateInput.value = res.visited_at.slice(0, 10);
        } else if (!newVisited) {
          it.visited_at = null;
          dateInput.value = "";
        }
        if (res && res.visit_count !== undefined) {
          it.visit_count = res.visit_count;
          if (countDisplay) countDisplay.textContent = String(res.visit_count);
        }
      } catch (e) {
        // 失敗したら元に戻す
        it.visited = !newVisited;
        card.classList.toggle("is-visited", !newVisited);
        btn.className = !newVisited ? "btn visited" : "btn";
        btn.textContent = !newVisited ? "訪問済✅（解除）" : "訪問済にする";
    
        let stampEl2 = card.querySelector(".stamp");
        if (!newVisited) {
          if (!stampEl2) {
            stampEl2 = document.createElement("div");
            stampEl2.className = "stamp";
            stampEl2.textContent = "VISITED";
            card.appendChild(stampEl2);
          }
        } else {
          if (stampEl2) stampEl2.remove();
        }
    
        dateRow.style.display = !newVisited ? "" : "none";
        // 訪問回数も元に戻す
        it.visit_count = oldCount;
        if (countDisplay) countDisplay.textContent = String(oldCount);
        alert("APIエラー: " + e.message);
      } finally {
        btn.disabled = false;
      }
    };
  }

  row.appendChild(btn);

  card.appendChild(row);

  // 訪問日行のセットアップ
  dateRow.className = "visit-date-row";
  dateRow.style.display = it.visited ? "" : "none";

  const dateLbl = document.createElement("span");
  dateLbl.className = "visit-date-label";
  dateLbl.textContent = "訪問日：";

  dateInput.type = "date";
  dateInput.className = "visit-date-input";
  dateInput.disabled = !state.loggedIn;
  if (it.visited_at) {
    dateInput.value = it.visited_at.slice(0, 10);
  }
  dateInput.onchange = async () => {
    if (!state.loggedIn) return;
    try {
      const res = await apiPut(`/api/aquariums/${it.id}/visited_at`, { visited_at: dateInput.value || null });
      if (res) it.visited_at = res.visited_at;
    } catch (e) {
      alert("日付の保存に失敗: " + e.message);
    }
  };

  dateRow.appendChild(dateLbl);
  dateRow.appendChild(dateInput);
  card.appendChild(dateRow);

  // 訪問回数行（ログイン中のみ）
  if (state.loggedIn) {
    const countRow = document.createElement("div");
    countRow.className = "visit-count-row";

    const countLbl = document.createElement("span");
    countLbl.className = "visit-count-label";
    countLbl.textContent = "訪問回数：";

    const minusBtn = document.createElement("button");
    minusBtn.type = "button";
    minusBtn.className = "count-btn";
    minusBtn.textContent = "−";

    countDisplay = document.createElement("span");
    countDisplay.className = "count-display";
    countDisplay.textContent = String(it.visit_count || 0);

    const plusBtn = document.createElement("button");
    plusBtn.type = "button";
    plusBtn.className = "count-btn";
    plusBtn.textContent = "＋";

    async function saveCount(newCount) {
      if (newCount < 0) return;
      const old = it.visit_count || 0;
      it.visit_count = newCount;
      countDisplay.textContent = String(newCount);
      try {
        await apiPut(`/api/aquariums/${it.id}/visit_count`, { visit_count: newCount });
      } catch (e) {
        it.visit_count = old;
        countDisplay.textContent = String(old);
        alert("保存に失敗: " + e.message);
      }
    }

    minusBtn.onclick = () => saveCount((it.visit_count || 0) - 1);
    plusBtn.onclick = () => saveCount((it.visit_count || 0) + 1);

    countRow.appendChild(countLbl);
    countRow.appendChild(minusBtn);
    countRow.appendChild(countDisplay);
    countRow.appendChild(plusBtn);
    card.appendChild(countRow);
  }

  const note = document.createElement("textarea");
  note.className = "note";
  note.placeholder = "メモ（例：混雑、推し、展示、感想）";
  note.value = it.note || "";
  note.disabled = !state.loggedIn;
if (!state.loggedIn) note.placeholder = "ログインするとメモできます";
  note.onchange = async () => {
    if (!state.loggedIn) return;
    try {
      await apiPut(`/api/aquariums/${it.id}/note`, { note: note.value });
    } catch (e) {
      alert("APIエラー: " + e.message);
    }
  };
  card.appendChild(note);
    // ===== Photos UI (logged in only) =====
    const photosWrap = document.createElement("div");
    photosWrap.className = "photos";
  
    const thumbs = document.createElement("div");
    thumbs.className = "thumbs";
    photosWrap.appendChild(thumbs);
  
    async function refreshPhotos() {
      thumbs.innerHTML = "";
      if (!state.loggedIn) {
        const msg = document.createElement("div");
        msg.className = "photos-guest";
        msg.textContent = "ログインすると写真を追加できます";
        thumbs.appendChild(msg);
        return;
      }
  
      try {
        const list = await apiGet(`/api/aquariums/${it.id}/photos`);
        for (const p of list) {
          const item = document.createElement("div");
          item.className = "thumb-item";
        
          const img = document.createElement("img");
          img.className = "thumb";
          img.src = p.url;
          img.loading = "lazy";
          item.appendChild(img);
        
          const del = document.createElement("button");
          del.type = "button";
          del.className = "thumb-del";
          del.textContent = "×";
          del.title = "削除";
          del.onclick = async (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!confirm("この写真を削除しますか？")) return;
        
            try {
              const res = await fetch(`/api/aquariums/${it.id}/photos/${p.id}`, {
                method: "DELETE",
                credentials: "same-origin",
                headers: { "X-CSRF-Token": state.csrfToken },
              });
              if (!res.ok) throw new Error(await res.text());
              await refreshPhotos();
            } catch (err) {
              alert("削除に失敗: " + err.message);
            }
          };
          item.appendChild(del);
        
          thumbs.appendChild(item);
        }
      } catch (e) {
        console.warn("photos fetch failed:", e);
      }
    }
  
  // アップロード input（非表示）
  const up = document.createElement("input");
  up.type = "file";
  up.accept = "image/*";
  up.className = "photo-input-hidden";
  up.disabled = !state.loggedIn;

  // 見た目用ボタン
  const pickBtn = document.createElement("button");
  pickBtn.type = "button";
  pickBtn.className = "photo-btn";
  pickBtn.textContent = state.loggedIn ? "写真を追加" : "ログインして写真を追加";

  // 未ログインでも押せるようにする（押したらログインへ）
  pickBtn.disabled = false;
  
  pickBtn.onclick = () => {
    if (!state.loggedIn) {
      location.href = "/login";
      return;
    }
  
    // 429対策：写真一覧は必要になった時だけ読む（初回だけ）
    if (!photosWrap.dataset.loaded) {
      photosWrap.dataset.loaded = "1";
      refreshPhotos();
    }
  
    up.click();
  };

  const hint = document.createElement("div");
  hint.className = "photo-hint";
  hint.textContent = "JPG / PNG / WEBP";

  up.onchange = async () => {
    if (!state.loggedIn) return;
    const file = up.files && up.files[0];
    if (!file) return;

    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await fetch(`/api/aquariums/${it.id}/photos`, {
        method: "POST",
        body: fd,
        credentials: "same-origin",
        headers: { "X-CSRF-Token": state.csrfToken },
      });
      if (!res.ok) throw new Error(await res.text());
      up.value = "";
      await refreshPhotos();
    } catch (e) {
      alert("写真アップロード失敗: " + e.message);
    }
  };

  photosWrap.appendChild(pickBtn);
  photosWrap.appendChild(hint);
  photosWrap.appendChild(up);
    card.appendChild(photosWrap);
  

  return card;
}



function render() {
  const q = $("q").value.trim();
  const list = $("list");
  list.innerHTML = "";

  const items = state.items.filter((x) => match(x, q)).filter(passesFilter);

  const ja = (a, b) => (a ?? "").toString().localeCompare((b ?? "").toString(), "ja");

  if (state.sort === "name") {
    items.sort((a, b) => ja(a.name, b.name));
  
  } else if (state.sort === "pref_plain") {
    // 地域分けしない「都道府県順」（デフォルト）
    items.sort((a, b) => {
      const ai = PREF_ORDER.indexOf(a.prefecture);
      const bi = PREF_ORDER.indexOf(b.prefecture);
  
      if (ai === -1 && bi === -1) return ja(a.name, b.name);
      if (ai === -1) return 1;
      if (bi === -1) return -1;
  
      if (ai !== bi) return ai - bi;
      return ja(a.name, b.name);
    });
  
  } else if (state.sort === "pref") {
    // 地域別
    items.sort((a, b) => {
      const ra = regionOf(a.prefecture);
      const rb = regionOf(b.prefecture);
      return ra.localeCompare(rb) || ja(a.name, b.name);
    });

  } else if (state.sort === "visit_count") {
    // 訪問回数順（未訪問は非表示）
    items = items.filter(x => x.visited);
    items.sort((a, b) => (b.visit_count || 0) - (a.visit_count || 0) || ja(a.name, b.name));

  } else if (state.sort === "visited_at") {
    // 訪問日順（新しい順）、未訪問は末尾
    items.sort((a, b) => {
      if (!a.visited_at && !b.visited_at) return ja(a.name, b.name);
      if (!a.visited_at) return 1;
      if (!b.visited_at) return -1;
      return b.visited_at.localeCompare(a.visited_at);
    });
  }

  // --- 描画（prefなら地域セクション、nameならフラット）
  if (state.sort === "pref") {
    const groups = new Map(); // region -> items[]
    for (const it of items) {
      const r = regionOf(it.prefecture);
      if (!groups.has(r)) groups.set(r, []);
      groups.get(r).push(it);
    }

    for (const r of REGION_ORDER) {
      const arr = groups.get(r);
      if (!arr || arr.length === 0) continue;

      if (state.regionOpen[r] === undefined) state.regionOpen[r] = false;

      const header = document.createElement("button");
      header.className = "regionHeadingBtn";
      header.type = "button";
      const done = arr.filter((x) => x.visited).length;
      header.textContent = `${state.regionOpen[r] ? "▼" : "▶"} ${r}（${done}/${arr.length}）`;      
      header.onclick = () => {
        state.regionOpen[r] = !state.regionOpen[r];
        render();
      };
      list.appendChild(header);

      const body = document.createElement("div");
      body.className = "regionBody";
      body.style.display = state.regionOpen[r] ? "" : "none";
      list.appendChild(body);

      for (const it of arr) {
        body.appendChild(renderCard(it));
      }
    }
  } else {
    for (const it of items) {
      list.appendChild(renderCard(it));
    }
  }

  // --- 地図更新（ここは必ず通す）
  console.log("sample item keys:", items[0] && Object.keys(items[0]));
  const mapKey = `${state.filter}|${state.pref}|${q}`;
  const shouldFit = state.lastMapKey !== mapKey;
  state.lastMapKey = mapKey;

  updateMap(items, { fit: shouldFit });
}

async function load() {
  const items = await apiGet(state.loggedIn ? "/api/aquariums" : "/api/public/aquariums");

  let stats = { visited: 0, total: items.length };

  if (state.loggedIn) {
    try {
      stats = await apiGet("/api/stats");
    } catch (e) {
      console.warn("stats取得失敗:", e);
    }
  }

  state.items = items;
  setPrefOptions(items);
  initMap();

  const visited = Number(stats.visited || 0);
  const total = Math.max(1, Number(stats.total || 0));
  const pct = Math.round((visited / total) * 100);

  const statsTextEl = document.getElementById("statsText");
  const statsPctEl = document.getElementById("statsPct");
  const barEl = document.getElementById("progressBar");

  if (statsTextEl && barEl) {
    statsTextEl.textContent = `訪問: ${visited} / ${total}`;
    if (statsPctEl) statsPctEl.textContent = `${pct}%`;
    barEl.style.width = `${pct}%`;
  } else {
    $("stats").textContent = `訪問: ${visited} / ${total}`;
  }

  render();
}

state.csrfToken = "";

async function initCsrf() {
  try {
    const res = await fetch("/api/csrf", { credentials: "same-origin" });
    const j = await res.json();
    state.csrfToken = j.token || "";
  } catch (e) {
    console.warn("csrf init failed", e);
  }
}

async function apiMe() {
  try {
    const res = await fetch("/api/me", { credentials: "same-origin" });
    if (!res.ok) return { logged_in: false };
    return await res.json();
  } catch {
    return { logged_in: false };
  }
}

function setLoginStatus(me) {
  const statusEl = document.getElementById("loginStatus");
  const loginBtn = document.getElementById("googleLogin");
  const logoutBtn = document.getElementById("logoutBtn");

  if (!statusEl || !loginBtn || !logoutBtn) return;

  // ★CTAも毎回ここで同期
  updateLoginCta(me);

  if (!me || !me.logged_in) {
    statusEl.textContent = "";
    loginBtn.style.display = "";
    logoutBtn.style.display = "none";
    return;
  }

  statusEl.textContent = `${me.name || me.email || me.user_id} でログイン中`;
  loginBtn.style.display = "none";
  logoutBtn.style.display = "";
}

function updateLoginCta(me) {
  const cta = document.getElementById("loginCta");
  const btn = document.getElementById("loginCtaBtn");
  if (!cta || !btn) return;

  const loggedIn = !!(me && me.logged_in);

  // 未ログインなら表示、ログイン中なら非表示
  cta.style.display = loggedIn ? "none" : "";

  btn.onclick = () => {
    location.href = "/login";
  };
}


function wireUI() {

  const qEl = $("q");
const searchBtn = $("searchBtn");

if (searchBtn) searchBtn.onclick = render;

// Enter でも検索できるように
if (qEl) {
  qEl.onkeydown = (e) => {
    if (e.key === "Enter") render();
  };
}

const loginBtn = document.getElementById("googleLogin");
if (loginBtn) loginBtn.onclick = () => { location.href = "/login"; };

const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) logoutBtn.onclick = async () => {
  try {
    await fetch("/logout", { credentials: "same-origin" });
  } finally {
    location.reload();
  }
};


  // ★追加：都道府県フィルター変更
  const prefSel = $("pref-filter");
  if (prefSel) {
    prefSel.onchange = () => {
      state.pref = prefSel.value || "";
      render();
    };
  }

  document.querySelectorAll(".chip").forEach((btn) => {
    btn.onclick = () => {
      state.filter = btn.dataset.filter;
      document.querySelectorAll(".chip").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      render();
    };
  });

  // 初期フィルタ
  document.querySelector('.chip[data-filter="all"]').classList.add("active");

 
  
}

wireUI();

(async () => {
  // まずCSRFトークン取得（ログイン前でもOK）
  await initCsrf();

  const me = await apiMe();
  state.loggedIn = !!(me && me.logged_in);
  setLoginStatus(me);

  load().catch((e) => alert("APIエラー: " + e.message));
})();


function initMap() {
  if (map) return;

  map = L.map("map", { zoomControl: true }).setView([36.2048, 138.2529], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // ★ここを差し替え
  markersLayer = L.layerGroup().addTo(map);
}


function updateMap(items, opts = { fit: true }) {
  if (!map) return;
  markersLayer.clearLayers();

  const pts = [];
  for (const it of items) {
    const lat = Number(it.lat ?? it.latitude);
    const lng = Number(it.lng ?? it.longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) continue;

    pts.push([lat, lng]);

    const label = it.name;                 // ★消した版
    const badge = it.visited ? "✅" : "⬜";
    const icon = L.divIcon({
      className: "",
      html: it.visited
        ? '<div class="marker visited"></div>'
        : '<div class="marker unvisited"></div>',
      iconSize: [16, 16],
    });

    const marker = L.marker([lat, lng], { icon })
      .addTo(markersLayer)
      .bindPopup(`${badge} ${label}<br>${it.prefecture}${it.city ? " / " + it.city : ""}`);
  }

  if (opts.fit && pts.length) {
    map.fitBounds(pts, { padding: [24, 24] });
  }
}

const sortSel = $("sort");
if (sortSel) {
  sortSel.onchange = () => {
    state.sort = sortSel.value;

    if (state.sort === "name") {
      state.pref = "";
      const prefSel = $("pref-filter");
      if (prefSel) prefSel.value = "";
    }
    render();
  };
}

document.addEventListener("DOMContentLoaded", () => {
  renderTimeline();
  const toggle = document.querySelector(".seo-toggle");
  const content = document.querySelector(".seo-content");
  if (!toggle || !content) return;

  toggle.onclick = () => {
    const open = content.style.display === "block";
    content.style.display = open ? "none" : "block";
    toggle.textContent = open
      ? "このアプリについて ▼"
      : "このアプリについて ▲";
  };
});




