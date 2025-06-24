<template>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form ref="stoageMetadataEdit">
        <v-card-title>Change metadata</v-card-title>
        <v-card-text>
          <v-select variant="outlined" density="comfortable" :items="itemsDevice" v-model="postData.deviceType"
            :rules="[r.required]" label="Select device type">
          </v-select>
          <v-select variant="outlined" density="comfortable" :items="itemsProtocol" v-model="postData.protocol"
            :rules="[r.required]" label="Select protocol">
          </v-select>
          <v-select variant="outlined" density="comfortable" :items="itemsRool" v-model="postData.rool"
            :rules="[r.required]" label="Select storage rool">
          </v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" v-on:click="submit">change</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { typeListNode } from '@/composables/nodes';
import { initNodeList, getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import notify from '@/composables/notify';
import { useStateStore } from '@/stores/state';

const dialogState = defineModel({ default: false })
const props = defineProps<{
  uuid: string
}>()

const state = useStateStore()

const itemsDevice = [
  { title: 'NVME SSD', value: 'nvme' },
  { title: 'SATA SSD', value: 'ssd' },
  { title: 'HDD', value: 'hdd' },
  { title: 'Ohter', value: 'other' }
]
const itemsProtocol = [
  { title: 'Local', value: 'local' },
  { title: 'NFS', value: 'nfs' },
  { title: 'Ohter', value: 'other' }
]
const itemsRool = [
  { title: 'VM Image', value: 'img' },
  { title: 'ISO installer', value: 'iso' },
  { title: 'Template Image', value: 'template' },
  { title: 'Cloud-init', value: 'init-iso' }
]

const itemsNodes = ref<typeListNode>(initNodeList)

const postData = reactive({
  uuid: '',
  rool: '',
  protocol: '',
  deviceType: ''
})

function submit() {
  postData.uuid = props.uuid
  apiClient.PATCH('/api/storages', { body: postData }).then((res) => {
    if (res.data) {
      notify("success", "Changed successfully", postData.uuid)
      dialogState.value = false
      state.trigger()
    }
  })
}


onMounted(async () => {
  itemsNodes.value = await getNode()
})


</script>
