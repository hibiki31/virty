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
            <v-col cols="12" sm="6" md="6" lg="4">
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
            <v-col>
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
  </div>
</template>

<script lang="ts" setup>
import { useRouter, useRoute } from 'vue-router';
import { apiClient } from '@/api';
import type { schemas } from '@/composables/schemas';
const route = useRoute()
import { onMounted } from 'vue';
import { useReloadListener } from '@/composables/trigger';

const data = ref<schemas['Network']>()
const dataXML = ref<schemas['NetworkXML']>()

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

useReloadListener(() => {
  reload()
})

onMounted(() => {
  reload()
})
</script>
