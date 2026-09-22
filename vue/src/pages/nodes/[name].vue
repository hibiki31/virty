<template>
  <div v-if="data">
    <v-card variant="flat">
      <v-card-item>
        <v-card-title>
          <v-icon left class="ma-3" :aria-label="nodeStatusLabel(data.status)" :color="getNodeStatusColor(data.status)" role="img">mdi-power-standby</v-icon>
          <span class="title">{{ data.name }}</span>
        </v-card-title>


        <v-card-subtitle>
          <span class="body ml-5">{{ data.description }}</span>
        </v-card-subtitle>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6" md="6" lg="3">
              <v-card prepend-icon="mdi-cube-outline" :title="t('pages.nodeDetail.sections.spec')">
                <v-table class="text-caption" density="compact">
                  <tbody align="right">
                    <tr v-for="item in getSpecList()" :key="item.title">
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
              <div v-for="item in getInfoListL()" :key="item.title">
                <p class="text-h6 pt-3">{{ item.title }}</p>
                <code-feild :text="item.value" type='Plaintext' :loading="!item.value"></code-feild>
              </div>
            </v-col>
            <v-col cols="12" lg="6">
              <div v-for="item in getInfoListR()" :key="item.title">
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
import { useRoute } from 'vue-router';
import { apiClient } from '@/api';
import type { paths } from '@/api/openapi'
const route = useRoute()
import { getNodeStatusColor } from '@/composables/nodes'
import { nodeStatusLabel, useLocalizedDocumentTitle } from '@/composables/i18n';
import { useI18n } from 'vue-i18n';
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n({ useScope: 'global' })
const auth = useAuthStore()

type typeNode = paths['/api/nodes/{name}']['get']['responses']['200']['content']['application/json']
type typeNodeInfo = paths['/api/nodes/{name}/info']['get']['responses']['200']['content']['application/json']

const data = ref<typeNode>()
const dataInfo = ref<typeNodeInfo>()

useLocalizedDocumentTitle(() => data.value?.name)

function reload() {
  if ('name' in route.params) {
    apiClient.GET('/api/nodes/{name}', {
      params: {
        path: { name: route.params.name },
        query: { admin: hasAdminScope(auth.scopes) },
      }
    }).then((res) => {
      if (res.data) {
        data.value = res.data
      }
    })

    apiClient.GET('/api/nodes/{name}/info', {
      params: {
        path: { name: route.params.name },
        query: { admin: hasAdminScope(auth.scopes) },
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
      { title: t('pages.nodeDetail.spec.status'), value: nodeStatusLabel(data.value?.status) },
      { title: t('pages.nodeDetail.spec.cpuModel'), value: data.value?.cpuGen },
      { title: t('pages.nodeDetail.spec.os'), value: data.value?.osName },
      { title: t('pages.nodeDetail.spec.qemuVersion'), value: data.value?.qemuVersion },
      { title: t('pages.nodeDetail.spec.libvirtVersion'), value: data.value?.libvirtVersion },

    ]
  }
}

function getInfoListR() {
  if (dataInfo) {
    return [
      { title: t('pages.nodeDetail.info.top'), value: dataInfo.value?.top },
      { title: t('pages.nodeDetail.info.free'), value: dataInfo.value?.free },
      { title: t('pages.nodeDetail.info.ipRoute'), value: dataInfo.value?.ipRoute },
      { title: t('pages.nodeDetail.info.ipNeighbor'), value: dataInfo.value?.ipNeigh },
      { title: t('pages.nodeDetail.info.ipAddress'), value: dataInfo.value?.ipAddress },
    ]
  }
}

function getInfoListL() {
  if (dataInfo) {
    return [
      { title: t('pages.nodeDetail.info.filesystem'), value: dataInfo.value?.dfH },
      { title: t('pages.nodeDetail.info.storage'), value: dataInfo.value?.lsblk },
      { title: t('pages.nodeDetail.info.netplan'), value: dataInfo.value?.netplanGet },
      { title: t('pages.nodeDetail.info.netfilter'), value: dataInfo.value?.iptables },
      { title: t('pages.nodeDetail.info.nat'), value: dataInfo.value?.iptablesNat },
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
