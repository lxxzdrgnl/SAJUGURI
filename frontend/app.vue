<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const config = useRuntimeConfig()

const menuOpen = ref(false)

function closeMenu() { menuOpen.value = false }

// 외부 클릭 시 닫기
onMounted(() => {
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (!target.closest('.menu-wrap')) closeMenu()
  })
})
</script>

<template>
  <div style="background: var(--bg-base); min-height: 100vh; display: flex; flex-direction: column;">
    <NuxtRouteAnnouncer />

    <!-- 네브바 -->
    <header class="app-header">
      <div class="app-header-inner">
        <NuxtLink to="/" class="app-logo ganji">
          <span style="color: var(--text-primary);">사주</span><span style="color: var(--accent);">구리</span>
        </NuxtLink>
        <div class="app-header-right">
          <template v-if="auth.isLoggedIn">
            <div class="menu-wrap">
              <button class="menu-btn" @click.stop="menuOpen = !menuOpen">
                <span class="menu-bar" />
                <span class="menu-bar" />
                <span class="menu-bar" />
              </button>
              <div v-if="menuOpen" class="menu-dropdown">
                <NuxtLink to="/my-profiles" class="menu-item" @click="closeMenu">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  내 만세력
                </NuxtLink>
                <div class="menu-divider" />
                <button class="menu-item menu-item-danger" @click="auth.logout(); closeMenu()">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  로그아웃
                </button>
              </div>
            </div>
          </template>
          <NuxtLink v-else to="/login" class="app-login-btn">로그인</NuxtLink>
        </div>
      </div>
    </header>

    <main style="flex: 1;">
      <NuxtPage />
    </main>

    <footer class="app-footer">
      <div class="app-footer-inner">
        <p>&copy; 2026 SAJUBON. All rights reserved.</p>
        <p class="app-footer-contact">
          <span>Contact:</span>
          <a href="mailto:pung4905@naver.com" class="app-footer-link">pung4905@naver.com</a>
        </p>
        <div class="app-footer-social">
          <a href="https://www.instagram.com/lxxzdrgnl" target="_blank" rel="noopener noreferrer" class="app-footer-social-link">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
            </svg>
          </a>
          <a href="https://github.com/lxxzdrgnl" target="_blank" rel="noopener noreferrer" class="app-footer-social-link">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.87 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
            </svg>
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--surface-1);
  border-bottom: 1px solid var(--border-subtle);
}

.app-header-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 24px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-logo {
  font-size: 1.2rem;
  font-weight: 700;
  text-decoration: none;
  letter-spacing: 0.05em;
}

.app-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ── 햄버거 메뉴 ── */
.menu-wrap {
  position: relative;
}

.menu-btn {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 36px;
  height: 36px;
  padding: 8px;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.15s;
}
.menu-btn:hover {
  background: var(--surface-2);
}
.menu-bar {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--text-secondary);
  border-radius: 2px;
}

.menu-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 160px;
  background: var(--surface-1);
  border: 1px solid var(--border-default);
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  overflow: hidden;
  z-index: 200;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  font-size: var(--fs-body);
  color: var(--text-primary);
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s;
  text-align: left;
}
.menu-item:hover {
  background: var(--surface-2);
}
.menu-item svg {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  flex-shrink: 0;
}
.menu-item-danger {
  color: #c04838;
}
.menu-item-danger svg {
  color: #c04838;
}
.menu-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 0;
}

.app-login-btn {
  font-size: var(--fs-label);
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  padding: 6px 14px;
  border: 1px solid var(--accent);
  border-radius: 8px;
  transition: all 0.15s;
}
.app-login-btn:hover {
  background: var(--accent);
  color: var(--surface-1);
}

.app-footer {
  margin-top: 48px;
  padding: 24px 32px;
  border-top: 1px solid var(--border-subtle);
  background: var(--surface-2);
  font-size: var(--fs-label);
  color: var(--text-muted);
}

.app-footer-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.app-footer-inner p { margin: 0; }

.app-footer-contact {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-footer-link {
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}
.app-footer-link:hover { color: var(--text-primary); }

.app-footer-social {
  display: flex;
  gap: 20px;
  margin-top: 8px;
}

.app-footer-social-link {
  color: var(--border-default);
  transition: color 0.2s;
}
.app-footer-social-link:hover { color: var(--text-muted); }
</style>
