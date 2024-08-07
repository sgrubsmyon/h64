import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/DashboardPage.vue')
      },
      {
        path: 'weather',
        component: () => import('pages/WeatherPage.vue'),
        children: [
          {
            path: 'overview',
            component: () => import('pages/WeatherOverview.vue')
          },
          {
            path: 'live',
            component: () => import('pages/WeatherLive.vue')
          },
          {
            path: 'archive',
            component: () => import('pages/WeatherArchive.vue')
          },
        ]
      },
      {
        path: 'pv',
        component: () => import('pages/PVPage.vue'),
        children: [
          {
            path: 'overview',
            component: () => import('pages/PVOverview.vue')
          },
          {
            path: 'live',
            component: () => import('pages/PVLive.vue')
          },
          {
            path: 'archive',
            component: () => import('pages/PVArchive.vue')
          },
        ]
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
