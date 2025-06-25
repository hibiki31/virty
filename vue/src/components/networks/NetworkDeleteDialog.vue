<template>
  <v-dialog v-model="model" persistent max-width="290">
    <v-card>
      <v-card-title class="headline">
        Delete Network
      </v-card-title>
      <v-card-text>{{ props.item?.name }}</v-card-text>
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
import type { typeListNetwork } from '@/composables/network';
import { apiClient } from '@/api';
import { useNotification } from '@kyvg/vue3-notification'
import { asyncSleep } from '@/composables/sleep';
const router = useRouter()

const { notify } = useNotification()
const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<typeListNetwork["data"][0]>,
    required: false,
  }
})

const loading = ref(false)


async function submit() {
  if (props.item) {
    loading.value = true
    const res = await apiClient.DELETE('/api/tasks/networks/{uuid}', { params: { path: { uuid: props.item.uuid } } })

    if (res.response.ok) {
      notify({
        type: 'success',
        title: 'Delete Network successful',
        text: 'Wait until the task is completed'
      })
      await asyncSleep(600)
      router.push("/networks")
    } else {
      notify({
        type: 'error',
        title: 'Delete Network failed'
      })
    }
    model.value = false
    loading.value = false
  }
}
</script>
