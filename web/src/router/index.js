import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '../store';
import VMList from '../views/VMList.vue';
import About from '../views/About.vue';
import Login from '../views/Login.vue';
import Logout from '../views/Logout.vue';
import VMDetail from '../views/VMDetail.vue';
import QueueList from '../views/QueueList.vue';
import NetworkList from '../views/NetworkList.vue';
import NodeList from '../views/NodeList.vue';
import StorageList from '../views/StorageList.vue';
import QueueDetail from '../views/QueueDetail.vue';
import ImageList from '../views/ImageList.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/vm',
    name: 'VMList',
    component: VMList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/',
    name: 'VMList',
    component: VMList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/queue',
    name: 'QueueList',
    component: QueueList,
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
    path: '/network',
    name: 'NetworkList',
    component: NetworkList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/node',
    name: 'NodeList',
    component: NodeList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/vm/:uuid',
    name: 'VMDetail',
    component: VMDetail,
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
  if (isAuthed || to.matched.some(record => !record.meta.requiresAuth)) {
    if ((to.name === 'Login' && isAuthed) || (to.name === 'Logout' && !isAuthed)) {
      next({ name: 'VMList' });
    } else {
      next();
    }
  } else {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  }
});

export default router;
