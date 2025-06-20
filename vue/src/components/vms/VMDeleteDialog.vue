<template>
  <v-dialog v-model="model" persistent max-width="290">
    <v-card>
      <v-card-title class="headline">
        Delete the VM
      </v-card-title>
      <v-card-text>Fails if VM is running. The disk image will remain.</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="success" text @click="model = false">
          Cancel
        </v-btn>
        <v-btn :loading="loading" color="error" text @click="submit()">
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { typeListVM } from '@/composables/vm'
import { reactive, ref } from 'vue';
import { defineProps, defineModel } from 'vue'
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'
import { asyncSleep } from '@/composables/sleep';
const router = useRouter()

const { notify } = useNotification()
const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<typeListVM["data"][0]>,
    required: false,
  }
})

const loading = ref(false)


async function submit() {
  if (props.item) {
    loading.value = true
    const res = await apiClient.DELETE('/api/tasks/vms/{uuid}', { params: { path: { uuid: props.item.uuid } } })

    if (res.response.ok) {
      notify({
        type: 'success',
        title: 'Delete VM successful',
        text: 'Wait until the task is completed'
      })
      await asyncSleep(600)
      router.push("/vms")
    } else {
      notify({
        type: 'error',
        title: 'Delete VM failed'
      })
    }
    model.value = false
    loading.value = false
  }
}
</script>
