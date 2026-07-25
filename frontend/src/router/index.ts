import { createRouter, createWebHistory } from 'vue-router';

import type { RankingType } from '@/types/api-requests';

declare module 'vue-router' {
  interface RouteMeta {
    readonly ranking?: {
      readonly type: RankingType;
      readonly title: string;
      readonly description: string;
      readonly supportsMinTotal: boolean;
    };
  }
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: (): Promise<unknown> => import('@/views/HomeView.vue') },
    {
      path: '/seasons',
      name: 'seasons',
      component: (): Promise<unknown> => import('@/views/SeasonCatalogView.vue'),
    },
    { path: '/search', name: 'search', component: (): Promise<unknown> => import('@/views/SearchView.vue') },
    {
      path: '/rankings/top-score',
      name: 'ranking-top-score',
      component: (): Promise<unknown> => import('@/views/RankingView.vue'),
      meta: {
        ranking: {
          type: 'top_score',
          title: '高分榜',
          description: '按最新评分排序，支持最低评价人数筛选。',
          supportsMinTotal: true,
        },
      },
    },
    {
      path: '/rankings/most-rated',
      name: 'ranking-most-rated',
      component: (): Promise<unknown> => import('@/views/RankingView.vue'),
      meta: {
        ranking: {
          type: 'most_rated',
          title: '最多人评价',
          description: '按最新评价人数排序。',
          supportsMinTotal: false,
        },
      },
    },
    {
      path: '/subjects/:bgmId',
      name: 'subject-detail',
      component: (): Promise<unknown> => import('@/views/SubjectDetailView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: (): Promise<unknown> => import('@/views/NotFoundView.vue'),
    },
  ],
});
