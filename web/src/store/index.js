import Vue from 'vue';
import Vuex from 'vuex';

import userData from './module/userData';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    userData
  }
});
