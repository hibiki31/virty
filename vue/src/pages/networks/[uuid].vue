<template>
  <div v-if="data">
    <v-card variant="flat">
      <network-delete-dialog :item="data" v-model="stateDeleteDialog"></network-delete-dialog>
      <v-card-item>
        <v-card-title>
          <span class="title">{{ data.name }}</span>
        </v-card-title>


        <v-card-subtitle>
          <span class="body ml-5">{{ data.description }}</span>
        </v-card-subtitle>

        <v-card-actions>
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
                    <tr v-for="item in getSpecList()">
                      <th>{{ item.title }}</th>
                      <td>{{ item.value }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card>
            </v-col>
          </v-row>
          <div v-for="item in getInfoList()">
            <p class="text-h6 pt-3">{{ item.title }}</p>
            <v-card color="grey-darken-3" :loading="!item.value">
              <v-card-text>
                <div class="font-mono text-caption" style="white-space: pre;">
                  {{ item.value }}
                </div>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>
      </v-card-item>
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

import { getNodeStatusColor } from '@/composables/nodes'

type typeNetwork = paths['/api/networks/{uuid}']['get']['responses']['200']['content']['application/json']
type typeNetworkInfo = paths['/api/networks/{uuid}/xml']['get']['responses']['200']['content']['application/json']

const data = ref<typeNetwork>()
const dataInfo = ref<typeNetworkInfo>()

const stateDeleteDialog = ref(false)

function reload() {
  if ('uuid' in route.params) {
    apiClient.GET('/api/networks/{uuid}', {
      params: {
        path: { uuid: route.params.uuid }
      }
    }).then((res) => {
      if (res.data) {
        data.value = res.data
        window.document.title = `Virty - ${res.data.name}`
      }
    })

    apiClient.GET('/api/networks/{uuid}/xml', {
      params: {
        path: { uuid: route.params.uuid }
      }
    }).then((res) => {
      if (res.data) {
        dataInfo.value = res.data
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

function getSpecList() {
  if (data) {
    return [
      { title: "Name: ", value: data.value?.name },
      { title: "UUID: ", value: data.value?.uuid },
      { title: "Node Name: ", value: data.value?.nodeName },
      { title: "Bridge Name: ", value: data.value?.bridge },
      { title: "Type: ", value: data.value?.type },
    ]
  }
}

function getInfoList() {
  if (dataInfo) {
    return [
      { title: "xml", value: dataInfo.value?.xml }
    ]
  }
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})
</script>
