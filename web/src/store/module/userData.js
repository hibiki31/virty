import Cookies from 'js-cookie';

const defaultState = {
  isLoaded: false,
  isAuthed: false,
  isAdmin: false,
  token: null,
  userId: null
};

const state = Object.assign({}, defaultState);

const mutations = {
  RESET_USER_DATA(state) {
    Object.assign(state, defaultState);
    Cookies.remove('token');
  },
  UPDATE_AUTH_STATE(state, { token, userId }) {
    Object.assign(state, defaultState);
    Cookies.remove('token');
    state.isLoaded = true;
    if (token) {
      state.isAuthed = true;
      state.token = token;
      state.userId = userId;
      state.isAdmin = true;
      Cookies.set('token', token);
    }
  }
};

const actions = {
  resetUserData: ({ commit }) => {
    commit('RESET_USER_DATA');
  },
  updateAuthState: ({ commit }, userData) => {
    commit('UPDATE_AUTH_STATE', userData);
  }
};

export default {
  state,
  mutations,
  actions
};
