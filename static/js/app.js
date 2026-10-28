/**
 * Cube Tech Enterprises - Core JavaScript Interactive Controller
 */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getCsrfToken() {
  const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (tokenInput && tokenInput.value) {
    return tokenInput.value;
  }
  return getCookie('csrftoken') || '';
}

// Toast Notification
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none px-4';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const bgColor = type === 'success' ? 'bg-[#111111]' : (type === 'error' ? 'bg-[#E53935]' : 'bg-[#FFC928] text-black');
  const textColor = type === 'warning' ? 'text-black' : 'text-white';
  
  toast.className = `${bgColor} ${textColor} text-sm font-semibold px-4 py-3 rounded-xl shadow-xl flex items-center justify-between gap-3 transform transition-all duration-300 translate-y-[-10px] opacity-0 pointer-events-auto border border-white/10`;
  toast.innerHTML = `
    <div class="flex items-center gap-2">
      <span class="inline-block w-2 h-2 rounded-full ${type === 'success' ? 'bg-emerald-400' : (type === 'error' ? 'bg-white' : 'bg-black')}"></span>
      <span>${message}</span>
    </div>
    <button class="text-white/60 hover:text-white text-xs font-bold ml-2" onclick="this.parentElement.remove()">✕</button>
  `;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-[-10px]', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-[-10px]');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Add to Cart Functionality
async function addToCart(productId, variantId = null, quantity = 1, redirectToCheckout = false) {
  try {
    const response = await fetch('/cart/api/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        product_id: productId,
        variant_id: variantId,
        quantity: parseInt(quantity) || 1,
      })
    });

    const data = await response.json();
    if (data.success) {
      // Update badge counts across all cart icons
      document.querySelectorAll('.cart-badge-count').forEach(el => {
        el.textContent = data.cart_count;
        el.classList.remove('hidden');
      });

      if (redirectToCheckout) {
        window.location.href = '/checkout/';
      } else {
        showToast(data.message || 'Product added to cart!');
      }
    } else {
      showToast(data.error || 'Failed to add product to cart', 'error');
    }
  } catch (error) {
    console.error('Add to cart error:', error);
    showToast('Network error, please try again.', 'error');
  }
}

// Toggle Wishlist
async function toggleWishlist(productId, btnElement) {
  try {
    const response = await fetch('/wishlist/api/toggle/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ product_id: productId })
    });

    const data = await response.json();
    if (data.success) {
      if (btnElement) {
        const svg = btnElement.querySelector('svg');
        if (data.is_wishlisted) {
          btnElement.classList.add('text-[#E53935]');
          if (svg) svg.setAttribute('fill', '#E53935');
        } else {
          btnElement.classList.remove('text-[#E53935]');
          if (svg) svg.setAttribute('fill', 'none');
        }
      }
      // Update wishlist count
      document.querySelectorAll('.wishlist-badge-count').forEach(el => {
        el.textContent = data.wishlist_count;
      });
      showToast(data.message);
    }
  } catch (err) {
    console.error('Wishlist error:', err);
  }
}

// Product Detail Page: Tab switching
function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

  const targetContent = document.getElementById(`tab-content-${tabName}`);
  const targetBtn = document.getElementById(`tab-btn-${tabName}`);
  if (targetContent) targetContent.classList.remove('hidden');
  if (targetBtn) targetBtn.classList.add('active');
}

// Support Widget Toggle
function toggleSupportWidget() {
  const panel = document.getElementById('support-chat-panel');
  if (panel) {
    panel.classList.toggle('hidden');
  }
}

// Support message send
async function sendSupportMessage(event) {
  event.preventDefault();
  const input = document.getElementById('support-chat-input');
  const text = input ? input.value.trim() : '';
  if (!text) return;

  const messagesContainer = document.getElementById('support-messages-container');
  if (messagesContainer) {
    const userMsg = document.createElement('div');
    userMsg.className = 'flex justify-end mb-2';
    userMsg.innerHTML = `<div class="bg-[#E53935] text-white text-xs px-3 py-2 rounded-xl max-w-[80%]">${text}</div>`;
    messagesContainer.appendChild(userMsg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  if (input) input.value = '';

  try {
    const res = await fetch('/support/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    if (data.reply && messagesContainer) {
      setTimeout(() => {
        const replyMsg = document.createElement('div');
        replyMsg.className = 'flex justify-start mb-2';
        replyMsg.innerHTML = `<div class="bg-gray-100 text-gray-800 text-xs px-3 py-2 rounded-xl max-w-[80%]">${data.reply}</div>`;
        messagesContainer.appendChild(replyMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }, 500);
    }
  } catch (e) {
    console.error('Chat error:', e);
  }
}
