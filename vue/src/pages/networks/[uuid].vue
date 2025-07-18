<template>
  <v-card variant="flat" :loading="!data">
    <network-delete-dialog :item="data" v-model="stateDeleteDialog"></network-delete-dialog>
    <v-card-title>
      <span class="title">{{ data?.name }}</span>
    </v-card-title>
    <v-card-item v-if="data">
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
          <v-col xs="12" sm="12" md="6" lg="3">
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
          <!-- Port Group -->
          <v-col xs="12" sm="12" md="6" lg="3" v-if="data.type === 'openvswitch'">
            <v-card prepend-icon="mdi-cube-outline" title="Port Group">
              <v-table class="text-caption" density="compact">
                <thead>
                  <tr>
                    <th class="text-left">Name</th>
                    <th class="text-left">VLAN</th>
                    <th class="text-left">Default</th>
                    <th class="text-left"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in sortedPortgroups" :key="item.name">
                    <td>{{ item.name }}</td>
                    <td>{{ item.vlanId }}</td>
                    <td>{{ item.isDefault ? "YES" : "" }}</td>
                    <td>

                      <v-btn icon="mdi-delete" color="error" variant="plain" density="compact" size="small"
                        @click="deletePort(item.name)" :loading="deleting.has(item.name)"
                        :disabled="deleting.has(item.name)"></v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
              <v-divider></v-divider>
              <!-- VLAN ADD -->
              <v-card-text>
                <v-form ref="formRef" @submit.prevent="submitPort">
                  <v-row>
                    <v-col cols="6">
                      <v-text-field v-model="addVlan.name" persistent-placeholder label="Name" density="compact"
                        placeholder="dmz-network" type="text" variant="outlined" counter="16"
                        :rules="[r.required, r.limitLength16, r.characterRestrictions, r.firstCharacterRestrictions]"></v-text-field>
                    </v-col>
                    <v-col cols="6">
                      <v-text-field v-model="addVlan.vlanId" label="VLAN ID" density="compact" placeholder="810"
                        type="number" persistent-placeholder hide-spin-buttons variant="outlined"
                        :rules="[r.required, r.vlan]">
                        <template v-slot:append>
                          <v-btn icon="mdi-send" variant="plain" density="compact" color="primary" type="submit"
                            :loading="loading || hasAnyOverlap(uuidTasks, state.task_uuids)"></v-btn>
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col xs="12" sm="12" md="12" lg="6">
            <v-card prepend-icon="mdi-xml" title="Info">
              <v-card-text>
                <div v-for="item in getInfoList()">
                  <p class="text-h6 pt-3">{{ item.title }}</p>
                  <code-feild :text="item.value" type="XML" :loading="!item.value"></code-feild>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card-item>
  </v-card>
</template>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas';
import { apiClient } from '@/api';

import { useReloadListener } from '@/composables/trigger';
import { asyncSleep } from '@/composables/sleep';
import { itemsCPU } from '@/composables/vm';

const route = useRoute()
const state = useStateStore()

const loading = ref(false)
const deleting = ref<Set<string>>(new Set())
const data = ref<schemas['Network']>()
const dataXML = ref<schemas['NetworkXML']>()

const addVlan = ref<schemas['NetworkOVSForCreate']>({
  default: false,
  name: "",
  vlanId: null,
})

const uuidTasks = ref<string[]>([])

const stateDeleteDialog = ref(false)

const sortedPortgroups = computed(() =>
  [...data.value?.portgroups || []].sort((a, b) => Number(a.vlanId || 0) - Number(b.vlanId || 0)) // 昇順
)

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
        dataXML.value = res.data
      }
    })

  }
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
  if (dataXML.value) {
    return [
      { title: "XML", value: dataXML.value.xml }
    ]
  }
}

async function submitPort(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }
  if (!('uuid' in route.params)) {
    return
  }

  loading.value = true
  const res = await apiClient.POST('/api/tasks/networks/{uuid}/ovs', {
    params: {
      path: { uuid: route.params.uuid }
    },
    body: addVlan.value
  })


  if (res.data) {
    uuidTasks.value.push(
      ...res.data.flatMap(task =>
        typeof task.uuid === 'string' && task.uuid ? [task.uuid] : []
      ),
    )
  }
  asyncSleep(300)
  loading.value = false
}

const hasAnyOverlap = <T>(a: readonly T[], b: readonly T[]) =>
  a.some(x => b.includes(x))

async function deletePort(name: string) {
  if (!('uuid' in route.params)) return
  if (deleting.value.has(name)) return

  deleting.value.add(name)

  const res = await apiClient.DELETE('/api/tasks/networks/{uuid}/ovs/{name}', {
    params: {
      path: {
        uuid: route.params.uuid,
        name: name
      }
    }
  })
  await asyncSleep(1000)
  deleting.value.delete(name)
}


useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})
</script>

<style lang="sass" scoped>
  .hover-btn :deep(.v-icon)
    color: rgba(var(--v-theme-on-background), var(--v-disabled-opacity))
    text-decoration: none
    transition: .2s ease-in-out

    &:hover
      color: rgba(var(--v-theme-primary))
</style>
