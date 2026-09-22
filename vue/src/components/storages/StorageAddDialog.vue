<template>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form @submit.prevent="submit">
        <v-card-title>{{ t('dialogs.storageAdd.title') }}</v-card-title>
        <v-card-text>
          <div class="mb-5">
            {{ t('dialogs.storageAdd.help') }}
          </div>
          <v-text-field variant="outlined" density="comfortable" :label="t('dialogs.storageAdd.displayName')" v-model="postData.name"
            :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]" counter="64"
            class="mb-3"></v-text-field>
          <v-select variant="outlined" density="comfortable" :label="t('dialogs.storageAdd.selectNode')" :items="itemsNodes.data"
            class="mb-3" item-title="name" item-value="name" v-model="postData.nodeName" :rules="[r.required]">
          </v-select>
          <v-text-field variant="outlined" density="comfortable" :label="t('common.fields.path')" v-model="postData.path"
            :rules="[r.required]" counter="128" class="mb-3"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialogState = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn color="primary" type="submit" :loading="loading">{{ t('common.actions.add') }}</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import type { typeListNode } from '@/composables/nodes';
import { initNodeList, getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import notify, { apiErrorRef, notifyTask } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';
import { onMounted, reactive, ref } from 'vue';
import { useLocalizedRules } from '@/composables/rules';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()

const dialogState = defineModel({ default: false })
const loading = ref(false)

const itemsNodes = ref<typeListNode>(initNodeList)
const postData = reactive({
  name: '',
  path: '',
  nodeName: ''
})

async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  loading.value = true
  try {
    const res = await apiClient.POST('/api/tasks/storages', { body: postData })
    if (res.data) {
      notifyTask(res.data[0].uuid)
      dialogState.value = false
    } else if (res.error) {
      notify('error', translationRef('dialogs.storageAdd.failed'), apiErrorRef(res.error))
    }
  } catch {
    notify('error', translationRef('dialogs.storageAdd.failed'), translationRef('dialogs.storageAdd.unreachable'))
  } finally {
    loading.value = false
  }
}


onMounted(async () => {
  itemsNodes.value = await getNode()
})
</script>
