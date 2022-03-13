<template>
  <v-app>
    <notifications group="default" animation-type="velocity" position="top right" class="mt-13">
      <template slot="body" slot-scope="props">
        <v-alert
          :type="props.item.type"
          class="ma-3"
          border="left"
          elevation="7"
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
          <div>
            <v-btn
              :color="this.$store.state.userData.adminMode ? 'error' : 'primary'"
              outlined depressed small class="mt-2"
              :disabled="!this.$store.state.userData.isAdmin"
              @click="toggleAdminMode"
            >
              {{ this.$store.state.userData.adminMode ? "Administrator" : "General user" }}
            </v-btn>
          </div>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group active-class="primary--text text--primary">
          <!-- メニュー描画 -->
          <v-list-item :to="{ name: 'VMList' }">
            <v-list-item-icon>
              <v-icon>mdi-cube-outline</v-icon>
            </v-list-item-icon>
            <v-list-item-title>VM</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'NodeList' }">
            <v-list-item-icon>
              <v-icon>mdi-server</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Node</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'NetworkList' }">
            <v-list-item-icon>
              <v-icon>mdi-wan</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Network</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'StorageList' }">
            <v-list-item-icon>
              <v-icon>mdi-database</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Storage</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'ImageList' }">
            <v-list-item-icon>
              <v-icon>mdi-harddisk</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Image</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'FlavorList' }">
            <v-list-item-icon>
              <v-icon>mdi-tag-multiple</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Flavor</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'TicketList' }">
            <v-list-item-icon>
              <v-icon>mdi-ticket-confirmation</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Ticket</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'IssueanceList' }">
            <v-list-item-icon>
              <v-icon>mdi-ticket</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Issuance</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'Users' }">
            <v-list-item-icon>
              <v-icon>mdi-account</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Users</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'Groups' }">
            <v-list-item-icon>
              <v-icon>mdi-account-group</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Groups</v-list-item-title>
          </v-list-item>
          <v-list-item :to="{ name: 'TaskList' }">
            <v-list-item-icon>
              <v-icon>mdi-checkbox-multiple-marked-outline</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Task</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <v-divider class="pb-2"></v-divider>
      <span class="subtitle-2 ml-3">Develop by <a href="https://github.com/hibiki31" class="primary--text">@hibiki31</a></span>
      <span class="subtitle-2 ml-1">v{{this.version}}</span>
    </v-navigation-drawer>
    <v-app-bar color="primary" dark dense flat app clipped-left>
      <v-toolbar-title>Virty</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-progress-circular
        v-if="(taskCount != 0)"
        indeterminate
        size="24"
        color="error"
        :value=taskCount
      ></v-progress-circular>
      <v-btn v-if="$store.state.userData.isAuthed" :to="{name: 'Logout'}" text>
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>
    <v-main class="ma-5">
      <router-view ref="view"/>
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
    taskCount: 0,
    taskHash: null,
    taskChecking: false
  }),
  methods: {
    async task_check() {
      if (!this.$store.state.userData.isAuthed) {
        return;
      }
      if (!this.taskChecking) {
        this.taskChecking = true;
        await axios.get('/api/tasks/incomplete', {
          params: {
            update_hash: this.taskHash,
            admin: this.$store.state.userData.adminMode
          }
        }).then(async(response) => {
          if (this.taskHash !== response.data.task_hash && this.taskHash !== null && response.data.task_count < this.taskCount) {
            if ('reload' in this.$refs.view === true) {
              this.$refs.view.reload();
            }
          }
          this.taskHash = response.data.task_hash;
          this.taskCount = response.data.task_count;
          this.taskChecking = false;
          await this.task_check();
        });
      }
    },
    toggleAdminMode() {
      this.$store.dispatch('toggleAdminMode');
      if ('reload' in this.$refs.view === true) {
        this.$refs.view.reload();
      }
    }
  },
  async mounted() {
    // ログイン後タスクチェック
    this.$store.subscribe((mutation, state) => {
      if (mutation.type === 'updateAuthState' && this.$store.state.userData.isAuthed) {
        this.task_check();
      }
    });
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
