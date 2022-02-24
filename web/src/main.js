import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import './mixins/utility';
import './mixins/rules';

import Cookies from 'js-cookie';
import axios from '@/axios/index';

import Notifications from 'vue-notification';
import velocity from 'velocity-animate';
import VueClipboard from 'vue-clipboard2';

Vue.config.productionTip = false;
Vue.config.devtools = true;
Vue.use(Notifications, { velocity });
Vue.use(VueClipboard);

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app');

const createApp = async() => {
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
