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
              <v-card prepend-icon="mdi-cube-outline" :title="t('pages.storageDetail.sections.spec')">
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
            <v-col>
              <v-card prepend-icon="mdi-xml" :title="t('pages.storageDetail.sections.json')">
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
import { formatNumber, useLocalizedDocumentTitle } from '@/composables/i18n';
import { useI18n } from 'vue-i18n';
import { hasAdminScope } from '@/composables/auth'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const data = ref<schemas['Storage']>()
const { t } = useI18n({ useScope: 'global' })

useLocalizedDocumentTitle(() => data.value?.name)

function reload() {
  if ('uuid' in route.params) {
    apiClient.GET('/api/storages/{uuid}', {
      params: {
        path: { uuid: route.params.uuid },
        query: { admin: hasAdminScope(auth.scopes) },
      }
    }).then((res) => {
      if (res.data) {
        data.value = res.data
      }
    })
  }
}

function getSpecList() {
  if (data.value) {
    return [
      { title: t('pages.storageDetail.spec.name'), value: data.value.name },
      { title: t('pages.storageDetail.spec.nodeName'), value: data.value.nodeName },
      { title: t('pages.storageDetail.spec.path'), value: data.value.path },
      { title: t('pages.storageDetail.spec.available'), value: t('pages.storageDetail.capacityGb', { value: formatNumber(data.value.available) }) },
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
