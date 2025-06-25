<template>
  <v-dialog width="400" v-model="model">
    <v-form ref="formRef" @submit.prevent="submit">
      <v-card>
        <v-card-title>ISO Image mount</v-card-title>
        <v-card-text>
          <v-checkbox label="Unmount" v-model="umount" hide-details></v-checkbox>
          <v-select :loading="loadingList" v-model="isoPath" :items="isoImages" v-if="!umount" append-icon="mdi-reload"
            variant="outlined" density="comfortable" @click:append="getIsoList"></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" type="submit">SUBMIT</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script setup lang="ts">
import { apiClient } from '@/api'
import type { schemas } from '@/composables/schemas'

const umount = ref(false)
const isoPath = ref<string>()

const loadingSubmit = ref(false)
const isoImages = ref<string[]>([])
const loadingList = ref(false)

const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['DomainDetail']>,
    required: false,
  },
  target: String
})

async function submit() {
  if (props.target) {

    if (props.item) {
      const res = await apiClient.PATCH("/api/tasks/vms/{uuid}/cdrom", {
        params: {
          path: { uuid: props.item.uuid }
        },
        body: {
          target: props.target,
          path: umount.value ? null : isoPath.value
        }
      })
      if (res.data) {
        model.value = false
      }
    }

  }
}


async function getIsoList() {
  loadingList.value = true
  if (model && props.item) {
    const res = await apiClient.GET("/api/images", {
      params: {
        query: {
          nameLike: ".iso",
          nodeName: props.item.nodeName
        }
      }
    })
    if (res.data) {
      isoImages.value = res.data.data.map((d) => d.path)
    }
  }
  loadingList.value = false
}

</script>
