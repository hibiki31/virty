const stateDefault = {
  projectId: null
};

// state初期値で初期化
const state = Object.assign({}, stateDefault);

const mutations = {
  setProjectId(state, projectId) {
    state.projectId = projectId;
  }
};

const actions = {
  setProjectId(context, projectId) {
    context.commit('setProjectId', projectId);
  }
};

export default {
  state,
  mutations,
  actions
};
