<script setup lang="ts">
import { STEM_HANJA, BRANCH_HANJA, STEM_ELEMENT as STEM_EL, BRANCH_ELEMENT as BRANCH_EL, iljuColor as elColor } from '~/utils/ganji'

export interface ProfileItem {
  id: number
  name: string
  birth_date: string
  birth_time: string | null
  calendar: string
  gender: string
  is_leap_month: boolean
  day_stem: string | null
  day_stem_element: string | null
  day_branch?: string | null
}

const props = defineProps<{
  profiles: ProfileItem[]
  profLoad: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  select: [profile: ProfileItem]
}>()
</script>

<template>
  <div class="profile-list-wrap">
    <div v-if="profLoad" class="center-state">
      <LoadingSpinner size="sm" />
    </div>
    <div v-else-if="profiles.length === 0" class="card empty-card">
      <p class="fs-body" style="color:var(--text-muted);">저장된 만세력이 없습니다.</p>
      <NuxtLink to="/profile" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
        만세력 보러가기
      </NuxtLink>
    </div>
    <div v-else class="profiles-list">
      <button
        v-for="p in profiles"
        :key="p.id"
        class="profile-card-item"
        :disabled="loading"
        @click="emit('select', p)"
      >
        <div class="profile-card-inner">
          <div class="profile-info">
            <p class="profile-name">
              {{ p.name }}
              <span
                v-if="p.day_stem"
                class="profile-name-ilju"
                :style="`color: ${elColor(p.day_stem_element ?? '')}`"
              >
                ({{ STEM_HANJA[p.day_stem] ?? p.day_stem }})
              </span>
            </p>
            <p class="profile-birth">
              {{ p.birth_date.replace(/-/g, '.') }} · {{ p.gender === 'male' ? '남' : '여' }}
              <template v-if="p.birth_time"> · {{ p.birth_time }}</template>
            </p>
            <p v-if="p.day_stem" class="profile-ilju">
              <span class="ilju-value" :style="`color: ${elColor(p.day_stem_element ?? '')}`">
                {{ STEM_HANJA[p.day_stem] ?? p.day_stem }}{{ BRANCH_HANJA[p.day_branch ?? ''] ?? '' }}
              </span>
            </p>
          </div>
          <div class="profile-illust-mini">
            <LoadingSpinner v-if="loading" size="sm" />
            <img v-else src="/profile-illust.webp" alt="" />
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.profile-list-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.center-state {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.empty-card {
  text-align: center;
  padding: 32px;
}
.profiles-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.profile-card-item {
  border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  overflow: hidden;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}
.profile-card-item:hover:not(:disabled) { background: var(--surface-2); }
.profile-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 20px 24px;
  gap: 16px;
}
.profile-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.profile-illust-mini {
  width: 72px;
  height: 72px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.profile-illust-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.profile-name {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.profile-name-ilju {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-ganji);
  letter-spacing: 0.03em;
}
.profile-birth {
  font-size: var(--fs-sub);
  color: var(--text-muted);
}
.profile-ilju {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}
.ilju-value {
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-ganji);
  letter-spacing: 0.05em;
}
</style>
