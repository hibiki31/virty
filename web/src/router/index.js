import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '../store';
import VMList from '../views/VMList.vue';
import Login from '../views/Login.vue';
import Logout from '../views/Logout.vue';
import VMDetail from '../views/VMDetail.vue';
import TaskList from '../views/TaskList.vue';
import NetworkList from '../views/NetworkList.vue';
import NodeList from '../views/NodeList.vue';
import StorageList from '../views/StorageList.vue';
import QueueDetail from '../views/QueueDetail.vue';
import ImageList from '../views/ImageList.vue';
import Empty from '../views/EmptyView.vue';
import Develop from '../views/Develop.vue';
import UserList from '../views/UserList.vue';
import GroupList from '../views/GroupList.vue';

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
    name: 'Root',
    component: VMList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/task',
    name: 'TaskList',
    component: TaskList,
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
    component: UserList
  },
  {
    path: '/groups',
    name: 'Groups',
    component: GroupList
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
