<template>
  <div v-if="data">
    <v-card variant="flat">
      <v-m-delete-dialog v-model="stateDeleteDialog" :item="data"></v-m-delete-dialog>
      <v-card-item>
        <v-card-title>
          <v-icon left class="ma-3" :color="getPowerColor(data.status)">mdi-power-standby</v-icon>
          <span class="title">{{ data.name }}</span>

        </v-card-title>


        <v-card-subtitle>
          <span class="body ml-5">{{ data.uuid }}</span>
        </v-card-subtitle>
      </v-card-item>

      <v-card-actions>
        <v-btn small dark class="ma-2" v-on:click="vmPowerOff(data.uuid)" color="grey">
          <v-icon left>mdi-power-standby</v-icon>PowerOFF
        </v-btn>

        <v-btn small dark class="ma-2" v-on:click="vmPowerOn(data.uuid)" color="primary">
          <v-icon left>mdi-power-standby</v-icon>PowerON
        </v-btn>

        <v-btn small class="ma-2" color="primary" @click="openVNC(data.uuid)" :disabled="data.vncPort === -1">
          <v-icon left>mdi-console</v-icon>Console
        </v-btn>
        <v-btn small dark class="ma-2" color="error" @click="stateDeleteDialog = true">
          <v-icon left>mdi-delete</v-icon>Delete
        </v-btn>
      </v-card-actions>

      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="6" lg="3">
            <v-card prepend-icon="mdi-cube-outline" title="Spec">
              <v-table class="text-caption" density="compact">
                <tbody align="right">
                  <tr>
                    <th>Status:</th>
                    <td>{{ data.status }}</td>
                  </tr>
                  <tr>
                    <th>vCPU:</th>
                    <td>{{ data.core }}</td>
                  </tr>
                  <tr>
                    <th>Memory:</th>
                    <td>{{ data.memory }} MB</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card>

            <v-card prepend-icon="mdi-server" title="Node" class="mt-5">
              <v-table class="text-caption" density="compact">
                <tbody align="right">
                  <tr>
                    <th>Name:</th>
                    <td>{{ data.node.name }}</td>
                  </tr>
                  <tr>
                    <th>Node IP:</th>
                    <td>{{ data.node.domain }}</td>
                  </tr>
                  <tr>
                    <th>Status:</th>
                    <td>{{ data.node.status }}</td>
                  </tr>
                  <tr>
                    <th>VNC Port:</th>
                    <td>{{ data.vncPort }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card>
          </v-col>
          <v-col cols="12" sm="12" md="12" lg="9">
            <v-card prepend-icon="mdi-router-network" title="Network">
              <v-table>
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
                        <v-icon @click="">mdi-pencil</v-icon>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-table>
            </v-card>
            <v-card class="mt-5">
              <v-card-title class="subheading font-weight-bold">
                <v-icon>mdi-database</v-icon>Storage
              </v-card-title>
              <v-table>
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
                        <v-icon v-if="itemDisk.device == 'cdrom'"
                          @click="openCDRomDialog(itemDisk.target)">mdi-pencil</v-icon>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-table>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts" setup>
import { useRouter, useRoute } from 'vue-router';
import { apiClient } from '@/api';
import type { paths } from '@/api/openapi'
const router = useRouter()
const route = useRoute()
import { onMounted } from 'vue';
import { useReloadListener } from '@/composables/trigger';

import { vmPowerOff, vmPowerOn, openVNC, getPowerColor } from '@/composables/vm';

type typeVM = paths['/api/vms/{uuid}']['get']['responses']['200']['content']['application/json']
const data = ref<typeVM>()

const stateDeleteDialog = ref(false)

function reload() {
  console.debug("vm detail reload")
  if ('uuid' in route.params) {
    console.debug(route.params.uuid)
    apiClient.GET('/api/vms/{uuid}', {
      params: {
        path: { uuid: route.params.uuid }
      }
    }).then((res) => {
      if (res.data) {
        data.value = res.data
        window.document.title = `Virty - ${res.data.name}`
      }
    })
  }
}



function openCDRomDialog(target: string | null | undefined) {
  // this.$refs.domainCDRomDialog.openDialog(target, this.data.uuid, this.data.node.name);
}
function openDeleteDialog() {
  // this.$refs.domainDeleteDialog.openDialog(this.data.uuid);
}



function memoryChangeMethod() {
  // axios
  //   .put('/api/queue/vm/memory', { uuid: this.$route.params.uuid, memory: this.memoryValue })
  //   .then((res) => {
  //     if (res.status === 401) {
  //       this.$_pushNotice('An error occurred', 'error');
  //     } else if (res.status !== 200) {
  //       this.$_pushNotice('An error occurred', 'error');
  //       return;
  //     }
  //     this.$_pushNotice('Queueing change memory task', 'success');
  //   })
  //   .catch(async () => {
  //     await this.$_sleep(500);
  //     this.$_pushNotice('An error occurred', 'error');
  //   });
}
function cpuChangeMethod() {
  // axios
  //   .put('/api/queue/vm/cpu', { uuid: this.$route.params.uuid, cpu: this.cpuValue })
  //   .then((res) => {
  //     if (res.status === 401) {
  //       this.$_pushNotice('An error occurred', 'error');
  //     } else if (res.status !== 200) {
  //       this.$_pushNotice('An error occurred', 'error');
  //       return;
  //     }
  //     this.$_pushNotice('Queueing change cpu task', 'success');
  //   })
  //   .catch(async () => {
  //     await this.$_sleep(500);
  //     this.$_pushNotice('An error occurred', 'error');
  //   });
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})
</script>
