<template>
  <div>
    <DomainAddDialog ref="domainAddDialog"/>
    <domain-add-tickets-dialog ref="domainAddTicketsDialog"/>
    <domain-group-put ref="domainGroupPut" @reload="reload"/>
    <v-dialog width="300" v-model="dialog">
      <v-card>
        <v-card-title>Change VM owner</v-card-title>
        <v-card-text>
          <v-select
            :items="user"
            item-text="id"
            item-value="id"
            v-model="selectUserId"
            label="Select userid"
            dense
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue darken-1"
            text
            v-on:click="
              dialog = false;
              vmOwnerChange();
            "
            >Change</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-card>
      <v-card-actions>
        <v-btn
          v-on:click="this.vmListReload"
          small
          dark
          class="ma-2"
          color="primary"
          :loading="this.reloadLoading"
          v-if="this.$store.state.userData.adminMode"
        >
          <v-icon left>mdi-cached</v-icon>Reload List
        </v-btn>
        <v-btn
          v-on:click="$refs.domainAddTicketsDialog.openDialog()"
          small
          dark
          class="ma-2"
          color="primary"
        >
          <v-icon left>mdi-server-plus</v-icon>CREATE VM
        </v-btn>
        <v-btn
          v-on:click="this.openDomainAddDialog"
          small
          dark
          class="ma-2"
          color="primary"
          v-if="this.$store.state.userData.adminMode"
        >

          <v-icon left>mdi-server-plus</v-icon>CREATE VM Administration MODE
        </v-btn>
      </v-card-actions>
      <v-data-table
        :loading="tableLoading"
        :headers="headers"
        :items="list"
        :items-per-page="20"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100, 200, 300, 400, 500],
          showFirstLastPage: true,
        }"
        multi-sort
      >
        <template v-slot:[`item.uuid`]="{ item }" justify="right">
          <router-link
            :to="{ name: 'VMDetail', params: { uuid: item.uuid } }"
            style="font-family: monospace;"
            >{{ item.uuid }}</router-link
          >
        </template>

        <!-- ユーザカラム -->
        <template v-slot:[`item.ownerUserId`]="{ item }" justify="right">
          <v-icon
            left
            v-on:click="
              uuid = item.uuid;
              dialog = true;
            "
            :color="item.ownerUserId === null ? '' : 'primary'"
            >mdi-account</v-icon
          >
          <span>{{ item.ownerUserId === null ? "" : item.ownerUserId }}</span>
        </template>

        <template v-slot:[`item.ownerGroupId`]="{ item }" justify="right">
          <v-icon
            left
            v-on:click="$refs.domainGroupPut.openDialog(item)"
            :color="item.ownerGroupId === null ? '' : 'primary'"
            >mdi-account</v-icon
          >
          <span>{{ item.ownerGroupId === null ? "" : item.ownerGroupId }}</span>
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
                  <v-icon v-on:click="vmPowerOn(item.uuid)" color="primary"
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
import DomainAddDialog from '../conponents/domains/DomainAddDialog';
import DomainGroupPut from '../conponents/domains/DomainGroupPut.vue';
import DomainAddTicketsDialog from '../conponents/domains/DomainAddTicketsDialog.vue';

export default {
  name: 'VMList',
  components: {
    DomainAddDialog,
    DomainGroupPut,
    DomainAddTicketsDialog
  },
  data: function() {
    return {
      tableLoading: true,
      list: [],
      dialog: false,
      uuid: '',
      reloadLoading: false,
      selectUserId: '',
      headers: [
        { text: 'Status', value: 'status' },
        { text: 'name', value: 'name' },
        { text: 'node', value: 'nodeName' },
        { text: 'UUID', value: 'uuid' },
        { text: 'RAM', value: 'memory' },
        { text: 'CPU', value: 'core' },
        { text: 'userId', value: 'ownerUserId' },
        { text: 'groupId', value: 'ownerGroupId' }
      ],
      user: [],
      projects: []
    };
  },
  mounted: async function() {
    this.reload();
    axios.get('/api/users').then((response) => (this.user = response.data));
    axios.get('/api/projects').then((response) => (this.projects = response.data));
  },
  methods: {
    reload() {
      this.tableLoading = true;
      axios.get('/api/vms', { params: { admin: this.$store.state.userData.adminMode } }).then((response) => {
        this.list = response.data;
        this.tableLoading = false;
      });
    },
    openDomainAddDialog() {
      this.$refs.domainAddDialog.openDialog();
    },
    getPowerColor(statusCode) {
      if (statusCode === 1) return 'primary';
      else if (statusCode === 5) return 'grey';
      else if (statusCode === 7) return 'purple';
      else if (statusCode === 10) return 'red';
      else if (statusCode === 20) return 'purple';
      else return 'yellow';
    },
    vmListReload() {
      // this.reloadLoading = true;
      axios
        .put('/api/vms')
        .then(res => {
          this.$_pushNotice('Added a task. Please wait for it to complete.', 'success');
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    },
    vmPowerOff(uuid) {
      axios
        .patch('/api/vms', { uuid: uuid, status: 'off' })
        .then((res) => {
          if (res.status === 401) {
            this.$_pushNotice('Wrong userID or password', 'error');
          } else if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Queueing powewrOff task', 'success');
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    },
    vmPowerOn(uuid) {
      axios
        .patch('/api/vms', { uuid: uuid, status: 'on' })
        .then((res) => {
          if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Queueing powewrOn task', 'success');
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    },
    vmOwnerChange() {
      axios
        .patch('/api/vms/user', {
          userId: this.selectUserId,
          uuid: this.uuid
        })
        .then((res) => {
          if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
          } else {
            this.$_pushNotice('Change user successfull', 'success');
          }
          this.reload();
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
    }
  }
};
</script>
