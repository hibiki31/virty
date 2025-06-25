<template>
  <v-dialog v-model="model" width="auto" v-if="props.item">
    <v-card width="900">
      <v-card-item>
        <v-card-title>
          <v-icon :color="getMethodColor(props.item.method)">{{ getResourceIcon(props.item.resource) }}</v-icon>
          {{ props.item.method.toUpperCase() }} {{ props.item.resource.toUpperCase() }} {{
            props.item.object.toUpperCase() }}
        </v-card-title>

        <v-card-subtitle>
          {{ toJST(props.item.postTime) }}
        </v-card-subtitle>
      </v-card-item>

      <v-card-text>
        <p class="text-h6">Message</p>
        <code-feild :text="props.item.message" type="TEXT" :loading="false"></code-feild>

        <p class="text-h6">Request</p>
        <code-feild :text="JSON.stringify(props.item.request, null, 2)" type="json" :loading="false"></code-feild>

        <v-divider></v-divider>
        <p class="text-h6">Log</p>
        <code-feild :text="props.item.log" type="TEXT" :loading="false"></code-feild>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { typeListTask } from '@/composables/task'
import { toJST, getStatusColor, getTaskList, toFixedTow, getMethodColor, getResourceIcon } from '@/composables/task'


const model = defineModel({ default: false })

const props = defineProps({
  item: {
    type: Object as PropType<typeListTask["data"][0]>,
    required: false,
  }
})
</script>
