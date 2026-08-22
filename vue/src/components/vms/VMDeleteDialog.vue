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
import type { schemas } from '@/composables/schemas';
import { apiClient } from '@/api';
import notify from '@/composables/notify';
import { asyncSleep } from '@/composables/sleep';
const router = useRouter()

const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['DomainDetail']>,
    required: false,
  }
})

const loading = ref(false)


async function submit() {
  if (props.item) {
    loading.value = true
    try {
      const res = await apiClient.DELETE('/api/tasks/vms/{uuid}', { params: { path: { uuid: props.item.uuid } } })

      if (res.response.ok) {
        notify('success', 'Delete VM successful', 'Wait until the task is completed')
        model.value = false
        await asyncSleep(600)
        await router.push("/vms")
      } else if (res.error) {
        notify('error', 'Delete VM failed', res.error)
      }
    } catch {
      notify('error', 'Delete VM failed', 'Unable to reach the VM service')
    } finally {
      loading.value = false
    }
  }
}
</script>
