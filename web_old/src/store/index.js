import Vue from 'vue';
import Vuex from 'vuex';

import userData from './module/userData';
import appData from './module/appData';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    userData,
    appData
  }
});
