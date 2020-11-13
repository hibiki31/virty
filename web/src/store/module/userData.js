import Cookies from 'js-cookie';
import VueJwtDecode from 'vue-jwt-decode';

/*
stateは状態変数そのものの定義。
stateはどこからでも読み込めるが、代入はしない。
stateはmutationsからしか変更不可。
*/

// 初期値を定義
const stateDefault = {
  isLoaded: false,
  isAuthed: false,
  isAdmin: false,
  token: null,
  userId: null,
  timeOffcet: 0
};

// state初期値で初期化
const state = Object.assign({}, stateDefault);

const mutations = {
  resetAuthState(state) {
    Object.assign(state, stateDefault);
    Cookies.remove('token');
  },
  updateAuthState(state, responseData) {
    Object.assign(state, stateDefault);
    Cookies.remove('token');
    state.isLoaded = true;
    if (responseData) {
      const token = VueJwtDecode.decode(responseData.access_token);
      state.isAuthed = true;
      state.token = responseData.access_token;
      state.userId = token.sub;
      state.isAdmin = true;
      Cookies.set('token', responseData.access_token);
    }
  },
  setTimeOffcet(state, timeOffcet) {
    state.timeOffcet = timeOffcet;
    Cookies.set('timeOffcet', timeOffcet);
  }
};

const actions = {
  updateAuthState(context, responseData) {
    context.commit('updateAuthState', responseData);
  },
  setTimeOffcet(context, timeOffcet) {
    context.commit('setTimeOffcet', timeOffcet);
  }
};

export default {
  state,
  mutations,
  actions
};
