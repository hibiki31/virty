<template>
  <div>
    <DomainAddDialog ref="domainAddDialog"/>
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
        >
          <v-icon left>mdi-cached</v-icon>Reload
        </v-btn>
        <v-btn
          v-on:click="this.openDomainAddDialog"
          small
          dark
          class="ma-2"
          color="primary"
        >
          <v-icon left>mdi-server-plus</v-icon>ADD
        </v-btn>
      </v-card-actions>
      <v-data-table
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
                  <v-icon v-on:click="vmPowerOn(item.uuid)" color="blue"
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
import DomainAddDialog from '../conponents/dialog/DomainAddDialog';

export default {
  name: 'VMList',
  components: {
    DomainAddDialog
  },
  data: function() {
    return {
      list: [],
      dialog: false,
      uuid: '',
      reloadLoading: false,
      selectUserId: '',
      headers: [
        { text: 'Status', value: 'status' },
        { text: 'name', value: 'name' },
        { text: 'UUID', value: 'uuid' },
        { text: 'RAM', value: 'memory' },
        { text: 'CPU', value: 'core' },
        { text: 'userId', value: 'userId' },
        { text: 'groupId', value: 'groupId' }
      ],
      user: [],
      group: []
    };
  },
  mounted: async function() {
    axios.get('/api/vms').then((response) => (this.list = response.data));
    axios.get('/api/users').then((response) => (this.user = response.data));
    axios.get('/api/groups').then((response) => (this.group = response.data));
  },
  methods: {
    openDomainAddDialog() {
      this.$refs.domainAddDialog.openDialog();
    },
    getPowerColor(statusCode) {
      if (statusCode === 1) return 'blue';
      else if (statusCode === 5) return 'grey';
      else if (statusCode === 7) return 'purple';
      else if (statusCode === 10) return 'red';
      else if (statusCode === 20) return 'purple';
      else return 'yellow';
    },
    vmListReload() {
      this.reloadLoading = true;
      axios
        .put('/api/vms')
        .then(res => {
          this.$_pushNotice('Added a task!', 'success');
          axios
            .get(`/api/tasks/${res.data.uuid}`, { params: { polling: true, timeout: 30000 } })
            .then(res => {
              this.$_pushNotice('Finished a task!', 'success');
              axios.get('/api/vms').then((response) => (this.list = response.data));
              this.reloadLoading = false;
            })
            .catch(error => {
              this.$_pushNotice(error.response.data.detail, 'error');
              this.reloadLoading = false;
            });
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
        .put('/api/vm/' + this.uuid, {
          userId: this.selectUserId,
          action: 'changeUser'
        })
        .then((res) => {
          if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Change user', 'success');
          axios.get('/api/vm').then((response) => (this.list = response.data));
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    }
  }
};
</script>
