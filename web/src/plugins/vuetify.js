import Vue from 'vue';
import Vuetify from 'vuetify/lib';
// import colors from 'vuetify/lib/util/colors';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      dark: {
        primary: '#2E8C83',
        secondary: '#031926',
        accent: '#F23D91',
        error: '#F23064',
        info: '#F2B1A2',
        success: '#8FD9D9',
        warning: '#FFC107'
      }
    },
    dark: true
  }
});
