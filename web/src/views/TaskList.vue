<template>
<div class="task-list">
  <TaskDeleteDialog ref="taskDeleteDialog" @reload="reload"/>
  <v-card>
    <v-card-actions>
      <v-btn v-on:click="this.openTaskDeleteDialog" small dark class="ma-2" color="error">
        <v-icon left>mdi-server-remove</v-icon>Delete
      </v-btn>
    </v-card-actions>
    <v-data-table
      :headers="headers"
      :items="list"
      :items-per-page="10"
      :loading="listLoadig"
      :footer-props="{
      'items-per-page-options': [10, 20, 50, 100],
      showFirstLastPage: true,
        }"
      multi-sort
    >
      <template v-slot:[`item.id`]="{ item }" justify="right">
        <router-link :to="{name: 'QueueDetail',params: {uuid: item.id}}">{{ item.id}}</router-link>
      </template>
      <template v-slot:[`item.name`]="{ item }" justify="right">
        <router-link
          :to="{
        name: 'VMDetail',
        params: {
          uuid: item.uuid
      }}"
        >{{ item.name}}</router-link>
      </template>
      <template v-slot:[`item.userId`]="{ item }" justify="right">{{item.userId}}</template>
      <template v-slot:[`item.postTime`]="{ item }" justify="right">{{item.postTime | toJST}}</template>

      <template v-slot:[`item.resource`]="{ item }" justify="right">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon
            v-bind="attrs"
            v-on="on"
            :color="getMethodColor(item.method)"
            >{{getResourceIcon(item.resource)}}</v-icon>
          </template>
          <span>Json Param: {{ item.request }}</span>
        </v-tooltip>
        <span class="ml-3">{{item.method}}.{{item.resource}}.{{item.object}}</span>
      </template>

      <template v-slot:[`item.status`]="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon
            v-bind="attrs"
            v-on="on"
            left :color="getStatusColor(item.status)">mdi-check-circle</v-icon>
          </template>
          <span>{{ item.message }}</span>
        </v-tooltip>
        {{item.status}}
      </template>

      <template v-slot:[`item.runTime`]="{ item }">
        {{ item.runTime | toFixedTow}} s
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon
            v-bind="attrs"
            v-on="on"
            class="ml-5"
            @click="copyClipBoardCurl(item)"
            >mdi-code-json</v-icon>
          </template>
          <span>{{ item.request }}</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon
              v-bind="attrs"
              v-on="on"
              class="ml-5"
              @click="copyClipBoard(item.message)"
            >mdi-android-messages</v-icon>
          </template>
          <span>{{ item.message }}</span>
        </v-tooltip>
      </template>

    </v-data-table>
  </v-card>
</div>
</template>

<script>
import axios from '@/axios/index';
import moment from 'moment';
import TaskDeleteDialog from '../conponents/dialog/TaskDeleteDialog';

export default {
  name: 'TaskList',
  components: {
    TaskDeleteDialog
  },
  data: function() {
    return {
      list: [],
      listLoadig: true,
      headers: [
        { text: 'Status', value: 'status' },
        { text: 'PostTime', value: 'postTime' },
        { text: 'Request', value: 'resource' },
        { text: 'userId', value: 'userId' },
        { text: 'ID', value: 'uuid' },
        { text: 'TunTime', value: 'runTime' }
      ]
    };
  },
  mounted: function() {
    this.reload();
  },
  methods: {
    reload() {
      this.listLoadig = true;
      axios.get('/api/tasks', { params: { admin: this.$store.state.userData.adminMode } }).then((response) => (this.list = response.data));
      this.listLoadig = false;
    },
    copyClipBoard(text) {
      this.$copyText(text).then(function(e) {
        console.log(e);
      }, function(e) {
        console.log(e);
      });
    },
    methodTransration(method) {
      switch (method) {
        case 'add': return 'POST';
        case 'update': return 'PUT';
        case 'delete': return 'DELETE';
        case 'cahnge': return 'PATH';
      }
    },
    copyClipBoardCurl(item) {
      const comand = `curl -X '${this.methodTransration(item.method)}' \\
'${location.protocol}//${location.host}/api/${item.resource}/${item.object}' \\
-H 'accept: application/json' \\
-H 'Authorization: Bearer ${this.$store.state.userData.token}' \\
-d '${JSON.stringify(item.request)}'`;
      this.$copyText(comand).then(function(e) {
        console.log(e);
      }, function(e) {
        console.log(e);
      });
    },
    openTaskDeleteDialog() {
      this.$refs.taskDeleteDialog.openDialog();
    },
    getStatusColor(statusCode) {
      if (statusCode === 'finish') return 'primary';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'error';
      else return 'yellow';
    },
    getMethodColor(statusCode) {
      if (statusCode === 'post') return 'success';
      else if (statusCode === 'put') return 'primary';
      else if (statusCode === 'delete') return 'error';
      else return 'yellow';
    },
    getResourceIcon(resource) {
      if (resource === 'vm') return 'mdi-cube-outline';
      else if (resource === 'node') return 'mdi-server';
      else if (resource === 'storage') return 'mdi-database';
      else if (resource === 'network') return 'mdi-wan';
      else return 'mdi-help-rhombus';
    }
  },
  filters: {
    toJST: function(date) {
      return moment(date).add(9, 'hour').format('YYYY/MM/DD HH:mm');
    },
    toFixedTow: function(val) {
      if (isFinite(val)) {
        return Number(val).toFixed(2);
      }
      return 0;
    }
  }
};
</script>
