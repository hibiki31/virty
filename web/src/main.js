import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import './mixins/utility';

import Cookies from 'js-cookie';
import axios from '@/axios/index';

import Notifications from 'vue-notification';
import velocity from 'velocity-animate';

Vue.config.productionTip = false;

const createApp = async() => {
  new Vue({
    router,
    store,
    vuetify,
    render: h => h(App)
  }).$mount('#app');
  Vue.use(Notifications, { velocity });
  const token = Cookies.get('token');
  const timeOffcet = Cookies.get('timeOffcet');

  if (timeOffcet) {
    store.dispatch('setTimeOffcet', timeOffcet);
  }

  if (!token) {
    store.dispatch('updateAuthState', {});
    if (router.app._route.name === 'Login' && router.app._route.query.redirect) {
      router.push({ name: 'Login' });
    }
  } else {
    await axios
      .get('/api/auth/validate',
        {
          headers: {
            Authorization: 'Bearer ' + token
          }
        }
      )
      .then(res => {
        store.dispatch('updateAuthState', res.data);
        if (router.app._route.name === 'Login') {
          router.push(router.app._route.query.redirect || { name: 'VMList' });
        }
      })
      .catch(() => {
        store.dispatch('updateAuthState', {});
      });
  }
};

createApp();
