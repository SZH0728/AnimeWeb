<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { DEFAULT_PAGE, DEFAULT_PAGE_SIZE } from '@/router/route-params';
import { buildSearchQuery } from '@/utils/query-params';

import GlobalSearchForm from './GlobalSearchForm.vue';

const route = useRoute();
const router = useRouter();
const isMenuOpen = ref(false);

watch(
  (): string => route.fullPath,
  (): void => {
    isMenuOpen.value = false;
  },
);

function handleMenuToggle(): void {
  isMenuOpen.value = !isMenuOpen.value;
}

function handleNavigation(): void {
  isMenuOpen.value = false;
}

async function handleSearchSubmitted(keyword: string): Promise<void> {
  await router.push({
    name: 'search',
    query: Object.fromEntries(
      new URLSearchParams(buildSearchQuery({ query: keyword, page: DEFAULT_PAGE, pageSize: DEFAULT_PAGE_SIZE })),
    ),
  });
}
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-transparent bg-white shadow-[0_3px_8px_-5px_rgb(148_163_184_/_0.75)]">
    <div class="app-container py-3">
      <div class="navbar min-h-0 gap-3 p-0">
        <div class="navbar-start">
          <RouterLink class="text-2xl font-bold tracking-tight text-primary" to="/">AnimeWeb</RouterLink>
        </div>
        <nav aria-label="主导航" class="navbar-center hidden lg:flex">
          <ul class="menu menu-horizontal gap-1 p-0">
            <li><RouterLink to="/">首页</RouterLink></li>
            <li><RouterLink to="/seasons">季度目录</RouterLink></li>
            <li><RouterLink to="/rankings/top-score">高分榜</RouterLink></li>
            <li><RouterLink to="/rankings/most-rated">最多人评价</RouterLink></li>
          </ul>
        </nav>
        <div class="navbar-end ml-auto gap-3">
          <div class="hidden w-72 lg:block">
            <GlobalSearchForm @search-submitted="handleSearchSubmitted" />
          </div>
          <button
            aria-controls="mobile-navigation"
            :aria-expanded="isMenuOpen"
            aria-label="切换导航菜单"
            class="btn lg:hidden"
            type="button"
            @click="handleMenuToggle"
          >
            菜单
          </button>
        </div>
      </div>
      <div class="mt-3 lg:hidden">
        <GlobalSearchForm @search-submitted="handleSearchSubmitted" />
      </div>
      <nav
        v-if="isMenuOpen"
        id="mobile-navigation"
        aria-label="移动端主导航"
        class="mt-3 border-base-300 border-t pt-3 lg:hidden"
      >
        <ul class="menu menu-vertical w-full p-0">
          <li><RouterLink to="/" @click="handleNavigation">首页</RouterLink></li>
          <li><RouterLink to="/seasons" @click="handleNavigation">季度目录</RouterLink></li>
          <li><RouterLink to="/rankings/top-score" @click="handleNavigation">高分榜</RouterLink></li>
          <li><RouterLink to="/rankings/most-rated" @click="handleNavigation">最多人评价</RouterLink></li>
        </ul>
      </nav>
    </div>
  </header>
</template>
