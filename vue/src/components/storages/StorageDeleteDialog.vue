<template>
  <v-dialog v-model="model" max-width="400">
    <v-card>
      <v-form ref="formRef" @submit.prevent="submit">
        <v-card-title class="headline">
          Delete Storage
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the storage?
          <v-checkbox density="comfortable" :label="'Delete ' + props.item?.name" :rules="[r.requiredCheckbox]"
            color="error"></v-checkbox>
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
import * as r from '@/composables/rules';
import { defineProps, defineModel } from 'vue'
import { apiClient } from '@/api';
import notify, { notifyTask } from '@/composables/notify';
import { asyncSleep } from '@/composables/sleep';


const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['Storage']>,
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
    const res = await apiClient.DELETE('/api/tasks/storages/{uuid}', { params: { path: { uuid: props.item.uuid } } })
    await asyncSleep(800)

    if (res.data) {
      notifyTask(res.data[0].uuid)
      model.value = false
    }
    if (res.error) {
      notify('error', 'Delete Storage failed', res.error)
    }
    loading.value = false
  }
}
</script>
