<template>
  <v-dialog width="400" v-model="model">
    <v-card>
      <v-form @submit.prevent="submit">
        <v-card-title>{{ t('dialogs.imageDownload.title') }}</v-card-title>
        <v-card-text>
          <v-text-field variant="outlined" density="comfortable" :label="t('dialogs.imageDownload.downloadUrl')" v-model="postData.imageUrl"
            :rules="[r.required, r.isValidURL]" counter="64" class="mb-3"></v-text-field>
          <v-select variant="outlined" density="comfortable" :label="t('dialogs.imageDownload.selectNode')" :items="itemsNodes.data" class="mb-3"
            item-title="name" item-value="name" v-model="postData.nodeName" :rules="[r.required]">
          </v-select>
          <v-select variant="outlined" density="comfortable" :label="t('dialogs.imageDownload.selectStorage')" :items="itemsStorages.data"
            class="mb-3" item-title="name" item-value="uuid" v-model="postData.storageUuid" :rules="[r.required]">
            <template v-slot:item="{ props: itemProps, item }">
              <v-list-item v-bind="itemProps" :subtitle="t('dialogs.imageDownload.nodeSubtitle', { name: item.raw.nodeName })"></v-list-item>
            </template>
          </v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="model = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">{{ t('common.actions.add') }}</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas';
import { initNodeList, getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import notify, { apiErrorRef, notifyTask } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import { getStorageList, initStorageList, type typeListStorageQuery } from '@/composables/storage';
import { onMounted, reactive, ref, watch } from 'vue';
import { useLocalizedRules } from '@/composables/rules';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()

const model = defineModel({ default: false })
const loading = ref(false)

const itemsNodes = ref<schemas['NodePage']>(initNodeList)
const itemsStorages = ref<schemas['StoragePage']>(initStorageList)

const postData = reactive({
  imageUrl: '',
  nodeName: '',
  storageUuid: ''
})

async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }
  loading.value = true
  try {
    const res = await apiClient.POST('/api/tasks/images/download', {
      params: { query: { admin: true } },
      body: postData,
    })
    if (res.data) {
      notifyTask(res.data[0].uuid)
      model.value = false
    } else if (res.error) {
      notify('error', translationRef('dialogs.imageDownload.failed'), apiErrorRef(res.error))
    }
  } catch {
    notify('error', translationRef('dialogs.imageDownload.failed'), translationRef('dialogs.imageDownload.unreachable'))
  } finally {
    loading.value = false
  }
}


onMounted(async () => {
  itemsNodes.value = await getNode()
})

watch(postData, async () => {
  const queryStorage: typeListStorageQuery = {
    admin: true,
    limit: 999999,
    page: 1,
    nodeName: postData.nodeName
  }
  itemsStorages.value = await getStorageList(queryStorage)
})

</script>
