<template>
  <v-app>
    <notifications group="default" animation-type="velocity">
      <template slot="body" slot-scope="props">
        <v-alert
          :type="props.item.type"
          class="ma-3 mb-0"
          border="left"
          colored-border
        >
          <div class="d-flex align-center ml-3">
            <div class="body-2 mr-auto">{{ props.item.text }}</div>
          </div>
        </v-alert>
      </template>
    </notifications>
    <v-navigation-drawer v-if="this.$store.state.userData.isAuthed" permanent floating app clipped>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">{{userId}}</v-list-item-title>
          <v-list-item-subtitle>Administrator</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group active-class="primary--text text--primary">
          <!-- メニュー描画 -->
          <v-list-item v-for="item in navList" :key="item.title" :to="item.to">
            <v-list-item-icon>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <v-divider class="pb-2"></v-divider>
      <span class="subtitle-2 ml-3">Develop by <a href="https://github.com/hibiki31" class="blue--text">@hibiki31</a></span>
      <span class="subtitle-2 ml-1">v{{this.version}}</span>
    </v-navigation-drawer>
    <v-app-bar color="primary" dark dense flat app clipped-left>
      <v-toolbar-title>Virty</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn :to="{name: 'Logout'}" text>
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>
    <v-main class="ma-5">
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
    version: require('../package.json').version,
    userId: '',
    navList: [
      {
        to: { name: 'VMList' },
        title: 'VM',
        icon: 'mdi-cube-outline'
      },
      {
        to: { name: 'NodeList' },
        title: 'Node',
        icon: 'mdi-server'
      },
      {
        to: { name: 'NetworkList' },
        title: 'Network',
        icon: 'mdi-wan'
      },
      {
        to: { name: 'ImageList' },
        title: 'Image',
        icon: 'mdi-harddisk'
      },
      {
        to: { name: 'StorageList' },
        title: 'Storage',
        icon: 'mdi-database'
      },
      {
        to: { name: 'TaskList' },
        title: 'Task',
        icon: 'mdi-checkbox-multiple-marked-outline'
      }
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
