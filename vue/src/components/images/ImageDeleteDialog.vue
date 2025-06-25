<template>
  <v-dialog v-model="model" max-width="400">
    <v-card>
      <v-form ref="formRef" @submit.prevent="submit">
        <v-card-title class="headline">
          Delete Images
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the storage?
          <v-checkbox density="comfortable" :label="'Yes, Delete ' + props.item?.length + ' images'"
            :rules="[r.requiredCheckbox]" color="error"></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="success" text @click="model = false">
            Cancel
          </v-btn>
          <v-btn :loading="loading" color="error" text type="submit">
            Delete
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { schemas } from '@/composables/schemas';
import { apiClient } from '@/api';
import notify, { notifyTask } from '@/composables/notify';
import { asyncSleep } from '@/composables/sleep';


const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['Image'][]>,
    required: false,
  }
})

const loading = ref(false)


async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  if (props.item) {
    loading.value = true
    console.log(props.item)
    for (const v of props.item) {
      console.log(v)
      const res = await apiClient.DELETE('/api/tasks/storages/{uuid}/images/{name}', {
        params: { path: { uuid: v.storageUuid, name: v.name } }
      })
      if (res.data) {
        notifyTask(res.data[0].uuid)
        model.value = false
      }
      if (res.error) {
        notify('error', 'Delete Storage failed', res.error)
      }
    }
    apiClient.PUT('/api/tasks/images').then((res) => {
      if (res.data) {
        notify("success", "The task has been queued.", "")
      }
    })

    await asyncSleep(800)
    loading.value = false
  }
}
</script>
