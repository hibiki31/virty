<template>
  <div>
    <user-add-dialog ref="userAddDialog" @reload="reload"/>
    <v-card>
      <v-card-actions>
        <v-btn
          v-on:click="$refs.userAddDialog.openDialog()"
          small
          dark
          class="ma-2"
          color="primary"
        >
          <v-icon left>mdi-server-plus</v-icon>ADD
        </v-btn>
      </v-card-actions>
      <v-data-table
        :loading="tableLoading"
        :headers="headers"
        :items="user"
        :items-per-page="20"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100, 200, 300, 400, 500],
          showFirstLastPage: true,
        }"
        multi-sort
      >
        <template v-slot:[`item.scopes`]="{ item }" justify="right">
          <v-chip
            v-for="scope in item.scopes"
            :key="scope.name"
            class="ma-2"
            close
          >
            {{ scope.name }}
          </v-chip>
        </template>
        <template v-slot:[`item.groups`]="{ item }" justify="right">
          <v-chip
            v-for="group in item.groups"
            :key="group.id"
            class="ma-2"
            close
          >
            {{ group.id }}
          </v-chip>
        </template>

        <!-- ユーザカラム -->
        <template v-slot:[`item.userId`]="{ item }" justify="right">
          <v-icon
            v-if="item.userId !== null"
            left
            v-on:click="
              uuid = item.uuid;
              dialog = true;
            "
            color="primary"
            >mdi-account</v-icon
          >
          <v-icon
            v-else
            left
            v-on:click="
              uuid = item.uuid;
              dialog = true;
            "
            >mdi-account</v-icon
          >
          <span v-if="item.userId !== null">{{ item.userId }}</span>
          <span v-else>N/A</span>
        </template>

        <template v-slot:[`item.groupId`]="{ item }" justify="right">
          <v-icon left>mdi-account-multiple</v-icon>
          <span v-if="item.groupId !== null">{{ item.groupId }}</span>
          <span v-else>N/A</span>
        </template>

        <template v-slot:[`item.status`]="{ item }">
          <v-menu>
            <template v-slot:activator="{ on: menu, attrs }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on: tooltip }">
                  <v-icon
                    left
                    v-bind="attrs"
                    v-on="{ ...tooltip, ...menu }"
                    :color="getPowerColor(item.status)"
                    >mdi-power-standby</v-icon
                  >
                </template>
                <span>Power control</span>
              </v-tooltip>
            </template>
            <v-card>
              <v-card-text>
                <div class="mb-3">
                  <v-icon v-on:click="vmPowerOn(item.uuid)" color="success"
                    >mdi-power-standby</v-icon
                  >
                </div>
                <v-icon v-on:click="vmPowerOff(item.uuid)" color="grey"
                  >mdi-power-standby</v-icon
                >
              </v-card-text>
            </v-card>
          </v-menu>
        </template>
        <template v-slot:[`item.memory`]="{ item }" justify="right">
          <v-icon left>mdi-memory</v-icon>
          {{ item.memory / 1024 }} G
        </template>
        <template v-slot:[`item.core`]="{ item }" justify="right">
          <v-icon left>mdi-cpu-64-bit</v-icon>
          {{ item.core }}
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import UserAddDialog from '../conponents/dialog/UserAddDialog.vue';

export default {
  name: 'VMList',
  components: {
    UserAddDialog
  },
  data: function() {
    return {
      tableLoading: true,
      headers: [
        { text: 'id', value: 'id' },
        { text: 'scopes', value: 'scopes' },
        { text: 'groups', value: 'groups' },
        { text: 'actions', value: 'actions' }
      ],
      user: [],
      group: []
    };
  },
  mounted: async function() {
    this.reload();
  },
  methods: {
    async reload() {
      this.tableLoading = true;
      await axios.get('/api/users').then((response) => (this.user = response.data));
      await axios.get('/api/groups').then((response) => (this.group = response.data));
      this.tableLoading = false;
    }
  }
};
</script>
