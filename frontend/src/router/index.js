import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ListView from "@/views/ListView.vue";
import SearchView from "@/views/SearchView.vue";
import NotFoundView from "@/views/NotFoundView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {'title': '首页'}
    },
    {
      path: '/list',
      name: 'list',
      component: ListView,
      meta: {'title': '排名'}
    },
    {
      path: '/search/:keyword',
      name: 'search',
      component: SearchView,
      meta: {'title': '搜索'}
    },
    {
      path: '/anime/:id',
      name: 'detail',
      component: () => import('../views/DetailView.vue'),
      meta: {'title': '详情'}
    },
    {
      path: '/:pathMatch(.*)*',
      name: '404',
      component: NotFoundView,
      meta: {'title': '404'}
    }
  ]
})


router.beforeEach((to, from, next) => {
  window.document.title = to.meta.title
  next()
})


export default router
