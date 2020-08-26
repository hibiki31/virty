<template>
  <v-app>
    <notifications group="default" animation-type="velocity">
      <template slot="body" slot-scope="props">
        <v-alert
          :type="props.item.type"
          :icon="props.item.data.icon"
          :color="props.item.data.color"
          class="ma-3 mb-0"
          border="left"
        >
          <div class="d-flex align-center ml-3">
            <div class="body-2 mr-auto">{{ props.item.text }}</div>
            <v-btn icon x-small class="ml-0" @click="props.close">
              <v-icon small>fa-times</v-icon>
            </v-btn>
          </div>
        </v-alert>
      </template>
    </notifications>
    <v-navigation-drawer permanent floating app clipped>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">{{userId}}</v-list-item-title>
          <v-list-item-subtitle>Administrator</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group active-class="primary--text text--primary">
          <v-list-item :to="{name: 'VMList'}">
            <v-list-item-icon>
              <v-icon>mdi-home</v-icon>
            </v-list-item-icon>
            <v-list-item-title>VM</v-list-item-title>
          </v-list-item>

          <v-list-item :to="{name: 'NetworkList'}">
            <v-list-item-icon>
              <v-icon>mdi-wan</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Network</v-list-item-title>
          </v-list-item>

          <v-list-item :to="{name: 'ImageList'}">
            <v-list-item-icon>
              <v-icon>mdi-harddisk</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Image</v-list-item-title>
          </v-list-item>

          <v-list-item :to="{name: 'StorageList'}">
            <v-list-item-icon>
              <v-icon>mdi-database</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Storage</v-list-item-title>
          </v-list-item>

          <v-list-item :to="{name: 'QueueList'}">
            <v-list-item-icon>
              <v-icon>mdi-checkbox-multiple-marked-outline</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Queue</v-list-item-title>
          </v-list-item>

          <v-list-item :to="{name: 'NodeList'}">
            <v-list-item-icon>
              <v-icon>mdi-server</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Node</v-list-item-title>
          </v-list-item>

          <v-list-item :to="{name: 'Logout'}" class="mt-10">
            <v-list-item-icon>
              <v-icon>mdi-account</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>

        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar color="primary" dark dense flat app clipped-left>
      <v-app-bar-nav-icon @click="drawer = true"></v-app-bar-nav-icon>
      <v-toolbar-title>Virty</v-toolbar-title>
    </v-app-bar>
    <v-main class="ma-2">
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import axios from '@/axios/index';
import Cookies from 'js-cookie';

export default {
  name: 'App',

  data: () => ({
    userId: '',
    items: [
      { title: 'Home', icon: 'dashboard' },
      { title: 'About', icon: 'question_answer' }
    ]
  }),
  methods: {},
  async mounted() {
    axios.interceptors.request.use(
      (config) => {
        config.headers.Authorization = 'Bearer ' + Cookies.get('token');
        this.userId = this.$store.state.userData.userId;
        return config;
      },
      (err) => {
        return Promise.reject(err);
      }
    );
  }
};
</script>
