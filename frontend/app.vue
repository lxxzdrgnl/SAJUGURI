<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const config = useRuntimeConfig()
</script>

<template>
  <div style="background: var(--bg-base); min-height: 100vh; display: flex; flex-direction: column;">
    <NuxtRouteAnnouncer />

    <!-- 네브바 -->
    <header class="app-header">
      <div class="app-header-inner">
        <NuxtLink to="/profile" class="app-logo ganji">사주구리</NuxtLink>
        <div class="app-header-right">
          <template v-if="auth.isLoggedIn">
            <span class="app-user-email">{{ auth.user?.email }}</span>
            <button class="app-logout-btn" @click="auth.logout()">로그아웃</button>
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
  color: var(--text-primary);
  text-decoration: none;
  letter-spacing: 0.05em;
}

.app-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-user-email {
  font-size: var(--fs-label);
  color: var(--text-muted);
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

.app-logout-btn {
  font-size: var(--fs-label);
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}
.app-logout-btn:hover {
  background: var(--surface-3);
  color: var(--text-primary);
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
