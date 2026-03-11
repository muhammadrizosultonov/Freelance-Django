// FreelanceUZ - Main JavaScript

document.addEventListener('DOMContentLoaded', () => {

  // ========== NAVBAR SCROLL ==========
  const navbar = document.getElementById('navbar');
  const handleScroll = () => {
    navbar?.classList.toggle('scrolled', window.scrollY > 20);
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // ========== MOBILE MENU ==========
  const navToggle = document.getElementById('navToggle');
  const mobileMenu = document.getElementById('mobileMenu');

  navToggle?.addEventListener('click', () => {
    const isOpen = mobileMenu.classList.toggle('open');
    document.body.style.overflow = isOpen ? 'hidden' : '';
    const spans = navToggle.querySelectorAll('span');
    if (isOpen) {
      spans[0].style.transform = 'translateY(7px) rotate(45deg)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
    } else {
      spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });

  mobileMenu?.addEventListener('click', (e) => {
    if (e.target === mobileMenu) {
      mobileMenu.classList.remove('open');
      document.body.style.overflow = '';
      navToggle?.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });

  // ========== AUTO-DISMISS MESSAGES ==========
  document.querySelectorAll('.message').forEach((msg, i) => {
    setTimeout(() => {
      msg.style.transform = 'translateX(110%)';
      setTimeout(() => msg.remove(), 400);
    }, 4000 + i * 500);
  });

  // ========== ROLE SELECTOR ==========
  document.querySelectorAll('.role-option').forEach(option => {
    option.addEventListener('click', () => {
      document.querySelectorAll('.role-option').forEach(o => o.classList.remove('selected'));
      option.classList.add('selected');
      const input = option.querySelector('input');
      if (input) input.checked = true;
    });
  });

  // ========== PROFILE TABS ==========
  document.querySelectorAll('.profile-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      document.querySelectorAll('.profile-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => {
        c.style.display = c.dataset.content === target ? 'block' : 'none';
      });
      tab.classList.add('active');
    });
  });

  // ========== CHAT FUNCTIONALITY ==========
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const messagesContainer = document.getElementById('chatMessages');

  const sendMessage = () => {
    if (!chatInput) return;
    const text = chatInput.value.trim();
    if (!text) return;

    const msgEl = document.createElement('div');
    msgEl.className = 'message-group own';
    msgEl.innerHTML = `
      <div class="message-bubble">${escapeHtml(text)}</div>
      <span class="message-time">${getCurrentTime()}</span>
    `;
    messagesContainer?.appendChild(msgEl);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    messagesContainer?.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
  };

  sendBtn?.addEventListener('click', sendMessage);
  chatInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  chatInput?.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });

  // ========== CHAT LIST ITEMS ==========
  document.querySelectorAll('.chat-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      const dot = item.querySelector('.unread-dot');
      if (dot) dot.remove();
    });
  });

  // ========== ANIMATE ON SCROLL ==========
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-in').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // ========== PROGRESS BARS ANIMATION ==========
  const progressObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const fill = entry.target.querySelector('.progress-fill');
        if (fill) {
          const targetWidth = fill.dataset.width || '0%';
          setTimeout(() => { fill.style.width = targetWidth; }, 100);
        }
        progressObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.progress-bar').forEach(bar => {
    const fill = bar.querySelector('.progress-fill');
    if (fill) {
      const targetWidth = fill.style.width;
      fill.dataset.width = targetWidth;
      fill.style.width = '0%';
      progressObserver.observe(bar);
    }
  });

  // ========== HELPERS ==========
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }

  function getCurrentTime() {
    return new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' });
  }

  // ========== STAT COUNTER ANIMATION ==========
  document.querySelectorAll('.stat-value[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    let current = 0;
    const step = target / 40;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
      if (current >= target) clearInterval(timer);
    }, 30);
  });

  // ========== DROPDOWN ==========
  document.querySelectorAll('[data-dropdown-trigger]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const target = document.getElementById(trigger.dataset.dropdownTrigger);
      target?.classList.toggle('open');
    });
  });

  document.addEventListener('click', () => {
    document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
  });

  // ========== FILE UPLOAD PREVIEW ==========
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function () {
      const previewId = this.dataset.preview;
      if (!previewId) return;
      const preview = document.getElementById(previewId);
      if (!preview) return;
      const file = this.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          preview.src = e.target.result;
          preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });
  });

});
