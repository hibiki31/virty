import Vue from 'vue';
import Vuetify from 'vuetify/lib';
// import colors from 'vuetify/lib/util/colors';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      dark: {
        primary: '#3aba8b',
        success: '#68cd86'
      },
      light: {
        primary: '#3aba8b',
        success: '#68cd86'
      }
    },
    dark: false
  }
});
