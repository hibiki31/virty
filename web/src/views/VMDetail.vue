<template>
  <div class="VMDetail">
    <DomainCDRomDialog ref="domainCDRomDialog" />
    <DomainDeleteDialog ref="domainDeleteDialog" />
    <domain-network-change ref="domainNetworkChange" />
    <v-dialog width="300" v-model="memoryDialog">
      <v-card>
        <v-card-title>Change Memory</v-card-title>
        <v-card-text>
          <v-select
            :items="memoryItems"
            :rules="[required]"
            v-model="memoryValue"
            label="Memory"
            dense
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text v-on:click="memoryDialog = false;memoryChangeMethod()">Change</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog width="300" v-model="cpuDialog">
      <v-card>
        <v-card-title>Change CPU</v-card-title>
        <v-card-text>
          <v-select
            :items="cpuItems"
            :rules="[required]"
            v-model="cpuValue"
            label="CPU"
            dense
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text v-on:click="cpuDialog = false;cpuChangeMethod()">Change</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
      <v-menu>
        <template v-slot:activator="{ on: menu, attrs }">
          <v-tooltip bottom>
            <template v-slot:activator="{ on: tooltip }">
              <v-icon
                left
                v-bind="attrs"
                v-on="{ ...tooltip, ...menu }"
                class="ma-3"
                :color="getPowerColor(data.status)"
                >mdi-power-standby</v-icon
              >
            </template>
            <span>Power control</span>
          </v-tooltip>
        </template>
        <v-card>
          <v-card-text>
            <div class="mb-3">
              <v-icon v-on:click="vmPowerOn(data.uuid)" color="primary"
                >mdi-power-standby</v-icon
              >
            </div>
            <v-icon v-on:click="vmPowerOff(data.uuid)" color="grey"
              >mdi-power-standby</v-icon
            >
          </v-card-text>
        </v-card>
      </v-menu>
    <span class="title">{{ data.name }}</span>
    <span class="body ml-5">{{ data.uuid }}</span>
    <v-row>
      <v-col cols="12" sm="6" md="6" lg="3">
        <v-card>
          <v-card-actions>
            <v-btn
              small
              class="ma-2"
              color="primary"
              @click="openVNC()"
              :disabled="data.vncPort === -1"
            >
              <v-icon left>mdi-console</v-icon>Console
            </v-btn>
            <v-btn
              @click="this.openDeleteDialog"
              small
              dark
              class="ma-2"
              color="error"
            >
              <v-icon left>mdi-delete</v-icon>Delete
            </v-btn>
          </v-card-actions>
        </v-card>
        <v-card class="mt-5">
          <v-card-title class="subheading font-weight-bold">
            Spec
          </v-card-title>
          <v-list class="body-2" dense>
            <v-list-item>
              <v-list-item-content>Memory</v-list-item-content>
              <v-list-item-content class="align-end">{{ data.memory / 1024 }} GB</v-list-item-content>
              <!-- <v-list-item-icon>
                <v-btn v-on:click="memoryDialog=true" small icon color="primary">
                  <v-icon>mdi-circle-edit-outline</v-icon>
                </v-btn>
              </v-list-item-icon> -->
            </v-list-item>

            <v-list-item>
              <v-list-item-content>CPU</v-list-item-content>
              <v-list-item-content class="align-end">{{ data.core }} Core</v-list-item-content>
              <!-- <v-list-item-icon>
                <v-btn v-on:click="cpuDialog=true" small icon color="primary">
                  <v-icon>mdi-circle-edit-outline</v-icon>
                </v-btn>
              </v-list-item-icon> -->
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="6" lg="3">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            Node
          </v-card-title>
          <v-list class="body-2" dense>
            <v-list-item>
              <v-list-item-content>Name</v-list-item-content>
              <v-list-item-content class="align-end">{{ data.node.name }}</v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-content>Node IP</v-list-item-content>
              <v-list-item-content class="align-end">{{ data.node.domain }}</v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-content>Node status</v-list-item-content>
              <v-list-item-content class="align-end">{{ data.node.status }}</v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-content>VNC Port</v-list-item-content>
              <v-list-item-content class="align-end">{{ data.vncPort }}</v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="12" lg="6">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            <v-icon>mdi-router-network</v-icon>Network
          </v-card-title>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Type</th>
                  <th class="text-left">MAC address</th>
                  <th class="text-left">Network Name</th>
                  <th class="text-left">Bridge Device</th>
                  <th class="text-left">oVS Port</th>
                  <th class="text-left">Target</th>
                  <th class="text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in data.interfaces" :key="`interface-${item.mac}`">
                  <td>{{ item.type }}</td>
                  <td>{{ item.mac }}</td>
                  <td>{{ item.network }}</td>
                  <td>{{ item.bridge }}</td>
                  <td>{{ item.port }}</td>
                  <td>{{ item.target }}</td>
                  <td>
                    <v-icon @click="$refs.domainNetworkChange.openDialog(data.uuid, item.mac, data.nodeName)">mdi-pencil</v-icon>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="12" lg="6">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            <v-icon>mdi-database</v-icon>Storage
          </v-card-title>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Device</th>
                  <th class="text-left">Type</th>
                  <th class="text-left">Source</th>
                  <th class="text-left">Target</th>
                  <th class="text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(itemDisk, index) in data.drives" :key="`itemDisk-${index}`">
                  <td>{{ itemDisk.device }}</td>
                  <td>{{ itemDisk.type }}</td>
                  <td>{{ itemDisk.source }}</td>
                  <td>{{ itemDisk.target }}</td>
                  <td>
                    <v-btn v-if="itemDisk.device=='cdrom'" icon v-on:click="openCDRomDialog(itemDisk.target)">
                      <v-icon>mdi-pen</v-icon>
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from '@/axios/index';
import DomainCDRomDialog from '../conponents/domains/DomainCDRomDialog';
import DomainDeleteDialog from '../conponents/domains/DomainDeleteDialog';
import DomainNetworkChange from '@/conponents/domains/DomainNetworkChange';

export default {
  name: 'VMDetail',
  components: {
    DomainCDRomDialog,
    DomainDeleteDialog,
    DomainNetworkChange
  },
  data: () => ({
    memoryDialog: false,
    memoryItems: [
      { text: '512MB', value: '512' },
      { text: '1GB', value: '1024' },
      { text: '2GB', value: '2048' },
      { text: '4GB', value: '4096' },
      { text: '8GB', value: '8192' },
      { text: '16GB', value: '16384' },
      { text: '32GB', value: '32768' }
    ],
    memoryValue: 0,
    cpuDialog: false,
    cpuItems: [
      { text: '1 Core', value: '1' },
      { text: '2 Core', value: '2' },
      { text: '4 Core', value: '4' },
      { text: '8 Core', value: '8' },
      { text: '12 Core', value: '12' },
      { text: '16 Core', value: '16' },
      { text: '24 Core', value: '24' }
    ],
    cpuValue: 0,
    data: {
      uuid: '',
      description: null,
      name: '',
      core: 16,
      memory: 16384,
      status: 1,
      userId: null,
      groupId: null,
      node: {
        name: '',
        description: '',
        domain: '',
        userName: '',
        port: 22,
        core: 40,
        memory: 128,
        cpuGen: '',
        osLike: '',
        osName: '',
        osVersion: '',
        status: 10,
        qemuVersion: '',
        libvirtVersion: ''
      },
      drives: [
        {
          device: '',
          type: '',
          file: null,
          target: ''
        }
      ],
      interface: [
        {
          type: '',
          mac: '',
          target: '',
          source: '',
          netwrok: null
        }
      ]
    }
  }),
  async mounted() {
    this.reload();
  },
  methods: {
    reload() {
      axios
        .get(`/api/vms/${this.$route.params.uuid}`)
        .then((res) => {
          this.data = res.data;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    openVNC() {
      window.open(`/novnc/vnc.html?resize=remote&autoconnect=true&path=novnc/websockify?token=${this.data.uuid}`);
    },
    openCDRomDialog(target) {
      this.$refs.domainCDRomDialog.openDialog(target, this.data.uuid, this.data.node.name);
    },
    openDeleteDialog() {
      this.$refs.domainDeleteDialog.openDialog(this.data.uuid);
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
    getPowerColor(statusCode) {
      if (statusCode === 1) return 'primary';
      else if (statusCode === 5) return 'grey';
      else if (statusCode === 7) return 'purple';
      else if (statusCode === 10) return 'red';
      else if (statusCode === 20) return 'purple';
      else return 'yellow';
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
    memoryChangeMethod() {
      axios
        .put('/api/queue/vm/memory', { uuid: this.$route.params.uuid, memory: this.memoryValue })
        .then((res) => {
          if (res.status === 401) {
            this.$_pushNotice('An error occurred', 'error');
          } else if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Queueing change memory task', 'success');
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    },
    cpuChangeMethod() {
      axios
        .put('/api/queue/vm/cpu', { uuid: this.$route.params.uuid, cpu: this.cpuValue })
        .then((res) => {
          if (res.status === 401) {
            this.$_pushNotice('An error occurred', 'error');
          } else if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Queueing change cpu task', 'success');
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    }
  }
};
</script>
