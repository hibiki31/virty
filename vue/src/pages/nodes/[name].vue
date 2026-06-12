<template>
  <div v-if="data">
    <v-card variant="flat">
      <v-card-item>
        <v-card-title>
          <v-icon left class="ma-3" :color="getNodeStatusColor(data.status)">mdi-power-standby</v-icon>
          <span class="title">{{ data.name }}</span>
        </v-card-title>


        <v-card-subtitle>
          <span class="body ml-5">{{ data.description }}</span>
        </v-card-subtitle>
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

          <v-row>
            <v-col cols="12" lg="6">
              <div v-for="item in getInfoListL()">
                <p class="text-h6 pt-3">{{ item.title }}</p>
                <code-feild :text="item.value" type='Plaintext' :loading="!item.value"></code-feild>
              </div>
            </v-col>
            <v-col cols="12" lg="6">
              <div v-for="item in getInfoListR()">
                <p class="text-h6 pt-3">{{ item.title }}</p>
                <code-feild :text="item.value" type='Plaintext' :loading="!item.value"></code-feild>
              </div>
            </v-col>
          </v-row>
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
import { getNodeStatusColor } from '@/composables/nodes'

type typeNode = paths['/api/nodes/{name}']['get']['responses']['200']['content']['application/json']
type typeNodeInfo = paths['/api/nodes/{name}/info']['get']['responses']['200']['content']['application/json']

const data = ref<typeNode>()
const dataInfo = ref<typeNodeInfo>()

const stateDeleteDialog = ref(false)

function reload() {
  if ('name' in route.params) {
    apiClient.GET('/api/nodes/{name}', {
      params: {
        path: { name: route.params.name }
      }
    }).then((res) => {
      if (res.data) {
        data.value = res.data
        window.document.title = `Virty - ${res.data.name}`
      }
    })

    apiClient.GET('/api/nodes/{name}/info', {
      params: {
        path: { name: route.params.name }
      }
    }).then((res) => {
      if (res.data) {
        dataInfo.value = res.data
      }
    })

  }
}

function getSpecList() {
  if (data) {
    return [
      { title: "Status: ", value: data.value?.status },
      { title: "CPU Model: ", value: data.value?.cpuGen },
      { title: "OS: ", value: data.value?.osName },
      { title: "QEMU version: ", value: data.value?.qemuVersion },
      { title: "Libvirt version: ", value: data.value?.libvirtVersion },

    ]
  }
}

function getInfoListR() {
  if (dataInfo) {
    return [
      { title: "Top (top -b -n 1|head -n 20)", value: dataInfo.value?.top },
      { title: "Free (free -h)", value: dataInfo.value?.free },
      { title: "IP Route (ip r)", value: dataInfo.value?.ipRoute },
      { title: "IP Neigh (ip n)", value: dataInfo.value?.ipNeigh },
      { title: "IP Address (ip a)", value: dataInfo.value?.ipAddress },
    ]
  }
}

function getInfoListL() {
  if (dataInfo) {
    return [
      { title: "Filesystem (df -h)", value: dataInfo.value?.dfH },
      { title: "Storage (lsblk)", value: dataInfo.value?.lsblk },
      { title: "Netplan (netplan get)", value: dataInfo.value?.netplanGet },
      { title: "Netfilter (iptables -L)", value: dataInfo.value?.iptables },
      { title: "NAT (iptables -L -t nat)", value: dataInfo.value?.iptablesNat },
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
