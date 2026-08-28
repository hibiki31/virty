<template>
  <div v-if="data">
    <v-card variant="flat">
      <v-m-delete-dialog v-model="stateDeleteDialog" :item="data"></v-m-delete-dialog>
      <v-m-network-change v-model="stateNetworkDialog" :item="data" :mac="changeMac"></v-m-network-change>
      <v-m-cdrom-change v-model="stateCdromDialog" :item="data" :target="deleteTarget"></v-m-cdrom-change>
      <v-card-item>
        <v-card-title>
          <v-icon left class="ma-3" :aria-label="vmStatusLabel(data.status)" :color="getPowerColor(data.status)" role="img">mdi-power-standby</v-icon>
          <span class="title">{{ data.name }}</span>

        </v-card-title>


        <v-card-subtitle>
          <span class="body ml-5">{{ data.uuid }}</span>
        </v-card-subtitle>
      </v-card-item>

      <v-card-actions>
        <v-btn small dark class="ma-2" v-on:click="vmPowerOff(data.uuid)" color="grey">
          <v-icon left>mdi-power-standby</v-icon>{{ t('pages.vmDetail.actions.powerOff') }}
        </v-btn>

        <v-btn small dark class="ma-2" v-on:click="vmPowerOn(data.uuid)" color="primary">
          <v-icon left>mdi-power-standby</v-icon>{{ t('pages.vmDetail.actions.powerOn') }}
        </v-btn>

        <v-btn small class="ma-2" color="primary" @click="openVNC(data.uuid)" :disabled="data.vncPort === -1">
          <v-icon left>mdi-console</v-icon>{{ t('pages.vmDetail.actions.console') }}
        </v-btn>
        <v-btn small dark class="ma-2" color="error" @click="stateDeleteDialog = true">
          <v-icon left>mdi-delete</v-icon>{{ t('pages.vmDetail.actions.delete') }}
        </v-btn>
      </v-card-actions>

      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="6" lg="3">
            <v-card prepend-icon="mdi-cube-outline" :title="t('pages.vmDetail.sections.spec')">
              <v-table class="text-caption" density="compact">
                <tbody align="right">
                  <tr>
                    <th>{{ t('pages.vmDetail.spec.status') }}</th>
                    <td>{{ vmStatusLabel(data.status) }}</td>
                  </tr>
                  <tr>
                    <th>{{ t('pages.vmDetail.spec.vcpu') }}</th>
                    <td>{{ formatNumber(data.core) }}</td>
                  </tr>
                  <tr>
                    <th>{{ t('pages.vmDetail.spec.memory') }}</th>
                    <td>{{ t('pages.vmDetail.memoryMb', { value: formatNumber(data.memory) }) }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card>

            <v-card prepend-icon="mdi-server" :title="t('pages.vmDetail.sections.node')" class="mt-5">
              <v-table class="text-caption" density="compact">
                <tbody align="right">
                  <tr>
                    <th>{{ t('pages.vmDetail.node.name') }}</th>
                    <td>{{ data.nodeName }}</td>
                  </tr>
                  <tr>
                    <th>{{ t('pages.vmDetail.node.ip') }}</th>
                    <td>{{ data.node.domain }}</td>
                  </tr>
                  <tr>
                    <th>{{ t('pages.vmDetail.node.status') }}</th>
                    <td>{{ nodeStatusLabel(data.node.status) }}</td>
                  </tr>
                  <tr>
                    <th>{{ t('pages.vmDetail.node.vncPort') }}</th>
                    <td>{{ data.vncPort == null ? t('common.values.unavailable') : formatNumber(data.vncPort) }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card>
          </v-col>
          <v-col cols="12" sm="12" md="12" lg="9">
            <v-card prepend-icon="mdi-router-network" :title="t('pages.vmDetail.sections.network')">
              <v-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-left">{{ t('pages.vmDetail.network.type') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.network.macAddress') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.network.networkName') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.network.bridgeDevice') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.network.ovsPort') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.network.target') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.network.actions') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in data.interfaces" :key="`interface-${item.mac}`">
                      <td>{{ item.type }}</td>
                      <td>{{ item.mac }}</td>
                      <td>
                        <router-link v-if="item.networkUuid" :to="'/networks/' + item.networkUuid">
                          {{ item.network }}
                        </router-link>
                        <span v-else>{{ item.network || '-' }}</span>
                      </td>
                      <td>{{ item.bridge }}</td>
                      <td>{{ item.port }}</td>
                      <td>{{ item.target }}</td>
                      <td>
                        <v-icon :aria-label="t('common.actions.edit')" role="button" tabindex="0"
                          @click="changeMac = item.mac || ''; stateNetworkDialog = true">mdi-pencil</v-icon>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-table>
            </v-card>
            <v-card class="mt-5">
              <v-card-title class="subheading font-weight-bold">
                <v-icon>mdi-database</v-icon>{{ t('pages.vmDetail.sections.storage') }}
              </v-card-title>
              <v-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-left">{{ t('pages.vmDetail.storage.device') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.storage.type') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.storage.size') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.storage.source') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.storage.target') }}</th>
                      <th class="text-left">{{ t('pages.vmDetail.storage.actions') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(itemDisk, index) in data.drives" :key="`itemDisk-${index}`">
                      <td>{{ itemDisk.device }}</td>
                      <td>{{ itemDisk.type }}</td>
                      <td>{{ formatStorageCapacity(itemDisk.capacityGb) }}</td>
                      <td>
                        <template v-if="itemDisk.source">
                          <v-chip size="small" variant="tonal" :aria-expanded="expandedStoragePaths.has(index)"
                            @click="toggleStoragePath(index)" @keydown.enter="toggleStoragePath(index)"
                            @keydown.space.prevent="toggleStoragePath(index)">
                            {{ getStorageFileName(itemDisk.source) }}
                          </v-chip>
                          <v-expand-transition>
                            <div v-if="expandedStoragePaths.has(index)" class="text-caption text-break mt-1 font-mono">
                              {{ itemDisk.source }}
                            </div>
                          </v-expand-transition>
                        </template>
                        <span v-else>-</span>
                      </td>
                      <td>{{ itemDisk.target }}</td>
                      <td>
                        <v-icon v-if="itemDisk.device == 'cdrom'" :aria-label="t('common.actions.edit')" role="button" tabindex="0"
                          @click="deleteTarget = itemDisk.target || ''; stateCdromDialog = true">mdi-pencil</v-icon>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-table>
            </v-card>
            <v-card class="mt-5">
              <v-card-title class="subheading font-weight-bold">
                <v-icon>mdi-xml</v-icon>{{ t('pages.vmDetail.sections.xml') }}
              </v-card-title>
              <v-expansion-panels>
                <v-expansion-panel>
                  <v-expansion-panel-title></v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <code-feild :text="dataXML?.xml" type="XML" :loading="false" class="ma-5"></code-feild>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts" setup>
import { useRoute } from 'vue-router';
import { apiClient } from '@/api';
const route = useRoute()
import type { schemas } from '@/composables/schemas';
import {
  formatNumber,
  nodeStatusLabel,
  useLocalizedDocumentTitle,
  vmStatusLabel,
} from '@/composables/i18n';
import { useI18n } from 'vue-i18n';
import {
  formatStorageCapacity,
  getPowerColor,
  getStorageFileName,
  openVNC,
  vmPowerOff,
  vmPowerOn,
} from '@/composables/vm';

const { t } = useI18n({ useScope: 'global' })

const data = ref<schemas['DomainDetail']>()
const dataXML = ref<schemas['DomainXML']>()

const stateDeleteDialog = ref(false)
const stateCdromDialog = ref(false)
const stateNetworkDialog = ref(false)
const deleteTarget = ref("")
const changeMac = ref("")
const expandedStoragePaths = ref(new Set<number>())

useLocalizedDocumentTitle(() => data.value?.name)

function toggleStoragePath(index: number) {
  const next = new Set(expandedStoragePaths.value)
  if (next.has(index)) {
    next.delete(index)
  } else {
    next.add(index)
  }
  expandedStoragePaths.value = next
}

async function reload() {
  console.debug("vm detail reload")
  if ('uuid' in route.params) {
    console.debug(route.params.uuid)
    const res = await apiClient.GET('/api/vms/{uuid}', {
      params: {
        path: { uuid: route.params.uuid }
      }
    })
    if (res.data) {
      data.value = res.data
    }

    const resXML = await apiClient.GET('/api/vms/{uuid}/xml', {
      params: {
        path: { uuid: route.params.uuid }
      }
    })
    if (resXML.data) {
      dataXML.value = resXML.data
    }
  }
}

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})
</script>
