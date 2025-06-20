import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '../store';

import VMList from '../views/VMList.vue';
import Login from '../views/Login.vue';
import Logout from '../views/Logout.vue';
import StorageList from '../views/StorageList.vue';
import QueueDetail from '../views/QueueDetail.vue';
import ImageList from '../views/ImageList.vue';
import Empty from '../views/EmptyView.vue';
import Develop from '../views/Develop.vue';
import UserList from '../views/UserList.vue';
import NetworkDetail from '@/views/NetworkDetail';
import NodeDetail from '@/views/NodeDetail';

import ListRouter from '@/router/listRouter.js';

Vue.use(VueRouter);

const routes = [
  ...ListRouter.routes,
  {
    path: '/vm',
    name: 'VMList',
    component: VMList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/nodes/:name',
    name: 'NodeDetail',
    component: NodeDetail,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/',
    name: 'Root',
    component: VMList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/storage',
    name: 'StorageList',
    component: StorageList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/image',
    name: 'ImageList',
    component: ImageList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/networks/:uuid',
    name: 'NetworkDetail',
    component: NetworkDetail,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/queue/:uuid',
    name: 'QueueDetail',
    component: QueueDetail,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/logout',
    name: 'Logout',
    component: Logout
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/empty',
    name: 'Empty',
    component: Empty
  },
  {
    path: '/develop',
    name: 'Develop',
    component: Develop
  },
  {
    path: '/users',
    name: 'Users',
    component: UserList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '*',
    redirect: 'VMList'
  }
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthed = store.state.userData.isAuthed;
  // ログインしているのにログインページに行く場合
  if (isAuthed && to.name === 'Login') {
    next({
      name: 'VMList'
    });
  }
  // 認証が必要なページに未認証でアクセスした場合
  if (!isAuthed && to.matched.some(record => record.meta.requiresAuth)) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  }
  next();
});

export default router;
