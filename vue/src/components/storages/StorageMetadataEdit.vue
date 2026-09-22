<template>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form ref="stoageMetadataEdit">
        <v-card-title>{{ t('dialogs.storageMetadata.title') }}</v-card-title>
        <v-card-text>
          <v-select variant="outlined" density="comfortable" :items="itemsDevice" v-model="postData.deviceType"
            :rules="[r.required]" :label="t('dialogs.storageMetadata.deviceType')">
          </v-select>
          <v-select variant="outlined" density="comfortable" :items="itemsProtocol" v-model="postData.protocol"
            :rules="[r.required]" :label="t('dialogs.storageMetadata.protocol')">
          </v-select>
          <v-select variant="outlined" density="comfortable" :items="itemsRool" v-model="postData.rool"
            :rules="[r.required]" :label="t('dialogs.storageMetadata.role')">
          </v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" v-on:click="submit">{{ t('common.actions.change') }}</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { typeListNode } from '@/composables/nodes';
import { initNodeList, getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import notify, { rawTextRef } from '@/composables/notify';
import { storageRoleLabel, translationRef } from '@/composables/i18n';
import { useStateStore } from '@/stores/state';
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useLocalizedRules } from '@/composables/rules';

const dialogState = defineModel({ default: false })
const props = defineProps<{
  uuid: string
}>()

const state = useStateStore()
const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()

const itemsDevice = computed(() => [
  { title: 'NVME SSD', value: 'nvme' },
  { title: 'SATA SSD', value: 'ssd' },
  { title: 'HDD', value: 'hdd' },
  { title: t('dialogs.storageMetadata.other'), value: 'other' }
])
const itemsProtocol = computed(() => [
  { title: t('dialogs.storageMetadata.local'), value: 'local' },
  { title: 'NFS', value: 'nfs' },
  { title: t('dialogs.storageMetadata.other'), value: 'other' }
])
const itemsRool = computed(() => [
  { title: storageRoleLabel('img'), value: 'img' },
  { title: storageRoleLabel('iso'), value: 'iso' },
  { title: storageRoleLabel('template'), value: 'template' },
  { title: storageRoleLabel('init-iso'), value: 'init-iso' }
])

const itemsNodes = ref<typeListNode>(initNodeList)

const postData = reactive({
  uuid: '',
  rool: '',
  protocol: '',
  deviceType: ''
})

function submit() {
  postData.uuid = props.uuid
  apiClient.PATCH('/api/storages', {
    params: { query: { admin: true } },
    body: postData,
  }).then((res) => {
    if (res.data) {
      notify("success", translationRef('dialogs.storageMetadata.changed'), rawTextRef(postData.uuid))
      dialogState.value = false
      state.trigger()
    }
  })
}


onMounted(async () => {
  itemsNodes.value = await getNode()
})


</script>
