const $ = (id) => document.getElementById(id);

let state = {
  items: [],
  filter: "all",
  pref: "",
  sort: "pref",
  lastMapKey: "",
  regionOpen: {},
};
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
  const res = await fetch(path, { headers: headers(), credentials: "same-origin" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
async function apiPut(path, body) {
  const res = await fetch(path, {
    method: "PUT",
    headers: headers(),
    credentials: "same-origin",
    body: JSON.stringify(body),
  });  
  if (!res.ok) throw new Error(await res.text());
  return res.json();
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

  const title = document.createElement("div");
  title.className = "title";
  title.textContent = it.name;
  card.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = `${it.prefecture}${it.city ? " / " + it.city : ""} ${it.location_raw ? " / " + it.location_raw : ""}`;
  card.appendChild(meta);

  const row = document.createElement("div");
  row.className = "row2";

  const btn = document.createElement("button");
  btn.className = it.visited ? "btn visited" : "btn";
  btn.textContent = it.visited ? "行った✅（解除）" : "行ったにする";
  btn.onclick = async () => {
    try {
      await apiPut(`/api/aquariums/${it.id}/visited`, { visited: !it.visited });
      await load(); // 再取得
    } catch (e) {
      alert("APIエラー: " + e.message);
    }
  };
  row.appendChild(btn);

  if (it.url) {
    const a = document.createElement("a");
    a.href = it.url;
    a.target = "_blank";
    a.rel = "noreferrer";
    a.className = "link";
    a.textContent = "公式/紹介ページ";
    row.appendChild(a);
  }

  card.appendChild(row);

  const note = document.createElement("textarea");
  note.className = "note";
  note.placeholder = "メモ（例：混雑、推し、展示、感想）";
  note.value = it.note || "";
  note.onchange = async () => {
    try {
      await apiPut(`/api/aquariums/${it.id}/note`, { note: note.value });
    } catch (e) {
      alert("APIエラー: " + e.message);
    }
  };
  card.appendChild(note);

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
  } else if (state.sort === "pref") {
    items.sort((a, b) => {
      const ai = PREF_ORDER.indexOf(a.prefecture);
      const bi = PREF_ORDER.indexOf(b.prefecture);

      if (ai === -1 && bi === -1) return ja(a.name, b.name);
      if (ai === -1) return 1;
      if (bi === -1) return -1;

      if (ai !== bi) return ai - bi;
      return ja(a.name, b.name);
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
  const key = getKey();

  const [items, stats] = await Promise.all([
    apiGet("/api/aquariums"),
    apiGet("/api/stats"),
  ]);

  state.items = items;

  // ★追加：都道府県セレクトを items から生成
  setPrefOptions(items);
  initMap();
  // stats -> progress
const visited = Number(stats.visited || 0);
const total = Math.max(1, Number(stats.total || 0));
const pct = Math.round((visited / total) * 100);

const statsTextEl = document.getElementById("statsText");
const statsPctEl = document.getElementById("statsPct");
const barEl = document.getElementById("progressBar");

if (statsTextEl && barEl) {
  statsTextEl.textContent = `訪問: ${visited} / ${stats.total}`;
  if (statsPctEl) statsPctEl.textContent = `${pct}%`;
  barEl.style.width = `${pct}%`;
} else {
  // フォールバック（HTML未更新でも壊れない）
  $("stats").textContent = `訪問: ${visited} / ${stats.total}`;
}

  render();
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
  const me = await apiMe();
  setLoginStatus(me);

  // 未ログインならロードしない（右上ログインから /login へ）
  if (!me.logged_in) return;

  // APIキーが必要な設計ならここでチェック（不要なら消してOK）
  // if (typeof getKey === "function" && !getKey()) return;

  load().catch((e) => alert("APIエラー: " + e.message));
})();


function initMap() {
  if (map) return;

  map = L.map("map", { zoomControl: true }).setView([36.2048, 138.2529], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // ★ここを差し替え
  markersLayer = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
    // 好みで：このズーム以上はクラスタしない
    disableClusteringAtZoom: 12,
  }).addTo(map);
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




