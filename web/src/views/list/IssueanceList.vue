<template>
<div class="ticket-list">
  <issueance-add ref="issuanceAdd" @reload="reload"/>
  <v-card>
    <v-card-actions>
           <v-btn v-on:click="$refs.issuanceAdd.openDialog()" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>ADD
        </v-btn>
    </v-card-actions>
    <v-data-table
      :headers="headers"
      :items="list"
      :items-per-page="10"
      :footer-props="{
      'items-per-page-options': [10, 20, 50, 100],
      showFirstLastPage: true,
        }"
      multi-sort
    >
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
      <template v-slot:[`item.date`]="{ item }" justify="right">{{item.postTime | toJST}}</template>

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
import IssueanceAdd from '../../conponents/tickets/IssueanceAdd.vue';

export default {
  name: 'TicketList',
  components: {
    IssueanceAdd
  },
  data: function() {
    return {
      list: [],
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Date', value: 'date' },
        { text: 'name', value: 'ticket.name' },
        { text: 'core', value: 'ticket.core' },
        { text: 'memory', value: 'ticket.memory' },
        { text: 'Publisher', value: 'issuedBy' }
      ]
    };
  },
  mounted: function() {
    this.reload();
  },
  methods: {
    reload() {
      axios.get('/api/tickets/issuances').then((response) => (this.list = response.data));
    },
    copyClipBoard(text) {
      this.$copyText(text).then(function(e) {
        console.log(e);
      }, function(e) {
        console.log(e);
      });
    },
    openTaskDeleteDialog() {
      this.$refs.taskDeleteDialog.openDialog();
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
