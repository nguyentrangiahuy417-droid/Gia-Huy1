// ============================================================
//  TELEGRAM WEB APP — GAME KEY SHOP
//  app.js  |  Tự chỉnh GAMES_DATA để thêm/sửa game & giá
// ============================================================

// ── Khởi tạo Telegram WebApp ──────────────────────────────
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
  // Màu nền đồng bộ với Telegram
  document.body.style.backgroundColor = tg.backgroundColor || '#0e0e13';
}

// ── DỮ LIỆU GAME (chỉnh tại đây) ────────────────────────
const GAMES_DATA = [
  {
    id: 1,
    title: 'Elden Ring',
    emoji: '⚔️',
    category: 'rpg',
    platform: 'Steam / PC',
    badge: 'HOT',
    desc: 'Thế giới mở rộng lớn, kết hợp cùng FromSoftware và George R.R. Martin. Trải nghiệm RPG hành động đỉnh cao.',
    keys: [
      { label: 'Standard Edition', price: 520000 },
      { label: 'Deluxe Edition',   price: 690000 },
    ],
  },
  {
    id: 2,
    title: 'GTA V + Online',
    emoji: '🚗',
    category: 'action',
    platform: 'Rockstar / PC',
    badge: 'HOT',
    desc: 'Thành phố Los Santos sống động. Bao gồm cả GTA Online với hàng nghìn giờ chơi.',
    keys: [
      { label: 'Standard',  price: 179000 },
      { label: 'Premium',   price: 259000 },
    ],
  },
  {
    id: 3,
    title: 'Cyberpunk 2077',
    emoji: '🤖',
    category: 'rpg',
    platform: 'Steam / PC',
    badge: 'NEW',
    desc: 'Night City tương lai – RPG hành động kết hợp Phantom Liberty DLC. Đồ họa next-gen.',
    keys: [
      { label: 'Base Game',             price: 399000 },
      { label: 'Ultimate Edition (+DLC)',price: 599000 },
    ],
  },
  {
    id: 4,
    title: 'FIFA 25',
    emoji: '⚽',
    category: 'sport',
    platform: 'EA / PC',
    badge: null,
    desc: 'Trải nghiệm bóng đá chân thực nhất. Ultimate Team, Career Mode và Volta Football.',
    keys: [
      { label: 'Standard',  price: 649000 },
      { label: 'Ultimate',  price: 999000 },
    ],
  },
  {
    id: 5,
    title: 'Minecraft Java',
    emoji: '🧱',
    category: 'strategy',
    platform: 'Mojang / PC',
    badge: null,
    desc: 'Build, craft và khám phá thế giới vô tận. Java Edition – moddable toàn diện.',
    keys: [
      { label: 'Java Edition', price: 389000 },
      { label: 'Java + Bedrock Bundle', price: 549000 },
    ],
  },
  {
    id: 6,
    title: 'Red Dead Redemption 2',
    emoji: '🤠',
    category: 'action',
    platform: 'Rockstar / Steam',
    badge: null,
    desc: 'Miền Tây hoang dã hùng vĩ. Câu chuyện Arthur Morgan – một trong những game hay nhất mọi thời đại.',
    keys: [
      { label: 'Standard Edition', price: 279000 },
      { label: 'Special Edition',  price: 369000 },
    ],
  },
  {
    id: 7,
    title: 'Hogwarts Legacy',
    emoji: '🪄',
    category: 'rpg',
    platform: 'Steam / PC',
    badge: 'NEW',
    desc: 'Thế giới Harry Potter mở rộng – RPG hành động đặt tại trường Hogwarts thế kỷ 19.',
    keys: [
      { label: 'Standard',  price: 429000 },
      { label: 'Deluxe',    price: 569000 },
    ],
  },
  {
    id: 8,
    title: 'Age of Empires IV',
    emoji: '🏰',
    category: 'strategy',
    platform: 'Steam / PC',
    badge: null,
    desc: 'Chiến lược thời gian thực kinh điển. 8 nền văn minh, chiến dịch lịch sử phong phú.',
    keys: [
      { label: 'Standard',           price: 299000 },
      { label: 'Anniversary Edition', price: 489000 },
    ],
  },
  {
    id: 9,
    title: 'Elden Ring DLC',
    emoji: '🌑',
    category: 'dlc',
    platform: 'Steam (yêu cầu base game)',
    badge: 'HOT',
    desc: 'Shadow of the Erdtree – DLC lớn nhất FromSoftware. Vùng đất mới, boss mới, vũ khí mới.',
    keys: [
      { label: 'Shadow of the Erdtree', price: 299000 },
    ],
  },
  {
    id: 10,
    title: 'Cyberpunk DLC',
    emoji: '🌆',
    category: 'dlc',
    platform: 'Steam (yêu cầu base game)',
    badge: 'NEW',
    desc: 'Phantom Liberty – chuyện gián điệp ly kỳ tại Dogtown. Cốt truyện mới, kết thúc mới.',
    keys: [
      { label: 'Phantom Liberty', price: 219000 },
    ],
  },
];

// ── STATE ────────────────────────────────────────────────
let activeCategory = 'all';
let searchQuery    = '';
let cart           = [];
let selectedGame   = null;
let selectedKey    = null;

// ── ELEMENTS ─────────────────────────────────────────────
const gameGrid    = document.getElementById('gameGrid');
const tabs        = document.getElementById('tabs');
const searchInput = document.getElementById('searchInput');
const cartBtn     = document.getElementById('cartBtn');
const cartCount   = document.getElementById('cartCount');

// Modal: detail
const modalOverlay = document.getElementById('modalOverlay');
const modalClose   = document.getElementById('modalClose');
const modalImg     = document.getElementById('modalImg');
const modalBadge   = document.getElementById('modalBadge');
const modalTitle   = document.getElementById('modalTitle');
const modalMeta    = document.getElementById('modalMeta');
const modalDesc    = document.getElementById('modalDesc');
const keyOptions   = document.getElementById('keyOptions');
const modalPrice   = document.getElementById('modalPrice');
const btnBuy       = document.getElementById('btnBuy');

// Modal: cart
const cartOverlay = document.getElementById('cartOverlay');
const cartClose   = document.getElementById('cartClose');
const cartList    = document.getElementById('cartList');
const cartTotalEl = document.getElementById('cartTotal');
const btnCheckout = document.getElementById('btnCheckout');

const toast = document.getElementById('toast');

// ── HELPERS ──────────────────────────────────────────────
const fmt = (n) => n.toLocaleString('vi-VN') + '₫';

let toastTimer;
function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
}

function haptic(type = 'light') {
  tg?.HapticFeedback?.impactOccurred(type);
}

// ── RENDER GAMES ─────────────────────────────────────────
function filteredGames() {
  return GAMES_DATA.filter(g => {
    const matchCat = activeCategory === 'all' || g.category === activeCategory;
    const q = searchQuery.toLowerCase();
    const matchQ = !q || g.title.toLowerCase().includes(q) || g.platform.toLowerCase().includes(q);
    return matchCat && matchQ;
  });
}

function renderGames() {
  const games = filteredGames();
  if (!games.length) {
    gameGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <div>Không tìm thấy game nào</div>
      </div>`;
    return;
  }

  gameGrid.innerHTML = games.map(g => {
    const minPrice = Math.min(...g.keys.map(k => k.price));
    const badgeHtml = g.badge === 'HOT'
      ? `<div class="badge-hot">🔥 HOT</div>`
      : g.badge === 'NEW'
      ? `<div class="badge-new">✨ NEW</div>`
      : '';

    return `
    <div class="game-card" data-id="${g.id}">
      <div class="game-card-img-placeholder">${g.emoji}</div>
      ${badgeHtml}
      <div class="game-card-body">
        <div class="game-card-title">${g.title}</div>
        <div class="game-card-platform">${g.platform}</div>
        <div>
          <span class="game-card-price">${fmt(minPrice)}</span>
        </div>
      </div>
    </div>`;
  }).join('');

  // Gắn click events
  gameGrid.querySelectorAll('.game-card').forEach(card => {
    card.addEventListener('click', () => {
      haptic('light');
      const id = parseInt(card.dataset.id);
      openGameModal(GAMES_DATA.find(g => g.id === id));
    });
  });
}

// ── TABS ─────────────────────────────────────────────────
tabs.addEventListener('click', e => {
  const tab = e.target.closest('.tab');
  if (!tab) return;
  haptic('light');
  tabs.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  activeCategory = tab.dataset.cat;
  renderGames();
});

// ── SEARCH ───────────────────────────────────────────────
searchInput.addEventListener('input', () => {
  searchQuery = searchInput.value;
  renderGames();
});

// ── GAME MODAL ───────────────────────────────────────────
function openGameModal(game) {
  selectedGame = game;
  selectedKey  = null;

  // Ảnh placeholder (emoji large)
  modalImg.style.display = 'none'; // Ẩn img tag, dùng emoji trong badge
  modalBadge.textContent = game.emoji + '  ' + (game.badge || game.category.toUpperCase());
  modalTitle.textContent = game.title;
  modalMeta.textContent  = `🖥️ ${game.platform}`;
  modalDesc.textContent  = game.desc;

  // Key options
  keyOptions.innerHTML = game.keys.map((k, i) => `
    <div class="key-option" data-idx="${i}">
      ${k.label}
      <br><strong style="color:var(--accent)">${fmt(k.price)}</strong>
    </div>
  `).join('');

  // Auto-select first option
  selectKey(0);

  keyOptions.querySelectorAll('.key-option').forEach(opt => {
    opt.addEventListener('click', () => {
      haptic('light');
      selectKey(parseInt(opt.dataset.idx));
    });
  });

  modalOverlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function selectKey(idx) {
  selectedKey = idx;
  keyOptions.querySelectorAll('.key-option').forEach((o, i) => {
    o.classList.toggle('selected', i === idx);
  });
  if (selectedGame) {
    modalPrice.textContent = fmt(selectedGame.keys[idx].price);
  }
}

function closeGameModal() {
  modalOverlay.classList.remove('open');
  document.body.style.overflow = '';
}

modalClose.addEventListener('click', () => { haptic('light'); closeGameModal(); });
modalOverlay.addEventListener('click', e => {
  if (e.target === modalOverlay) closeGameModal();
});

// ── ADD TO CART ──────────────────────────────────────────
btnBuy.addEventListener('click', () => {
  if (selectedGame === null || selectedKey === null) return;
  haptic('medium');

  const key = selectedGame.keys[selectedKey];
  cart.push({
    id:    Date.now(),
    game:  selectedGame.title,
    emoji: selectedGame.emoji,
    type:  key.label,
    price: key.price,
  });

  updateCartCount();
  showToast(`✅ Đã thêm: ${selectedGame.title} – ${key.label}`);
  closeGameModal();
});

function updateCartCount() {
  cartCount.textContent = cart.length;
  cartCount.style.background = cart.length ? 'var(--accent)' : 'var(--text3)';
}

// ── CART MODAL ───────────────────────────────────────────
cartBtn.addEventListener('click', () => { haptic('light'); openCart(); });

function openCart() {
  if (!cart.length) {
    cartList.innerHTML = `<div class="cart-empty">🛒<br>Giỏ hàng trống<br><span style="font-size:.8rem">Hãy chọn game bạn muốn mua</span></div>`;
    cartTotalEl.textContent = '0₫';
  } else {
    const total = cart.reduce((s, i) => s + i.price, 0);
    cartList.innerHTML = cart.map(item => `
      <div class="cart-item" data-id="${item.id}">
        <div class="cart-item-icon">${item.emoji}</div>
        <div class="cart-item-info">
          <div class="cart-item-name">${item.game}</div>
          <div class="cart-item-type">${item.type}</div>
        </div>
        <div class="cart-item-price">${fmt(item.price)}</div>
        <button class="cart-item-del" data-id="${item.id}">🗑</button>
      </div>
    `).join('');
    cartTotalEl.textContent = fmt(total);

    cartList.querySelectorAll('.cart-item-del').forEach(btn => {
      btn.addEventListener('click', () => {
        haptic('light');
        const id = parseInt(btn.dataset.id);
        cart = cart.filter(i => i.id !== id);
        updateCartCount();
        openCart(); // re-render
      });
    });
  }

  cartOverlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  cartOverlay.classList.remove('open');
  document.body.style.overflow = '';
}

cartClose.addEventListener('click', () => { haptic('light'); closeCart(); });
cartOverlay.addEventListener('click', e => {
  if (e.target === cartOverlay) closeCart();
});

// ── CHECKOUT ─────────────────────────────────────────────
btnCheckout.addEventListener('click', () => {
  if (!cart.length) return;
  haptic('success');

  const total = cart.reduce((s, i) => s + i.price, 0);
  const lines = cart.map(i => `• ${i.emoji} ${i.game} (${i.type}): ${fmt(i.price)}`).join('\n');
  const msg   = `🛒 Đơn hàng của tôi:\n\n${lines}\n\n💰 Tổng: ${fmt(total)}\n\n⏳ Vui lòng xác nhận và gửi thông tin thanh toán!`;

  if (tg) {
    // Gửi dữ liệu về bot Telegram
    tg.sendData(JSON.stringify({
      type:  'order',
      items: cart.map(i => ({ game: i.game, type: i.type, price: i.price })),
      total,
    }));
    tg.close();
  } else {
    // Dev fallback (không có Telegram)
    alert(msg);
  }
});

// ── INIT ─────────────────────────────────────────────────
renderGames();
updateCartCount();
