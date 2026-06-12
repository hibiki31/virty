<template>
  <div v-if="data">
    <v-card variant="flat">
      <v-card-item>
        <v-card-title>
          <span class="title">{{ data.name }}</span>
        </v-card-title>
        <v-card-subtitle>
          <span class="body ml-5">{{ data.uuid }}</span>
        </v-card-subtitle>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="12" md="6" lg="3">
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
              <v-card prepend-icon="mdi-xml" title="Json">
                <v-card-text>
                  <code-feild :text="JSON.stringify(data, null, 2)" type="JSON" :loading="false"></code-feild>
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
import type { schemas } from '@/composables/schemas';
import { apiClient } from '@/api';
import { useRoute } from 'vue-router';

const route = useRoute()
const data = ref<schemas['Storage']>()

const stateDeleteDialog = ref(false)

function reload() {
  if ('uuid' in route.params) {
    apiClient.GET('/api/storages/{uuid}', {
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

function getSpecList() {
  if (data.value) {
    return [
      { title: "Name: ", value: data.value.name },
      { title: "Node Name: ", value: data.value.nodeName },
      { title: "Path: ", value: data.value.path },
      { title: "Acailable: ", value: data.value.available + " GB" },
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
