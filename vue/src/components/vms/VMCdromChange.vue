<template>
  <v-dialog width="400" v-model="model">
    <v-form ref="formRef" @submit.prevent="submit">
      <v-card>
        <v-card-title>{{ $t('dialogs.vmCdrom.title') }}</v-card-title>
        <v-card-text>
          <v-checkbox :label="$t('dialogs.vmCdrom.unmount')" v-model="umount" hide-details></v-checkbox>
          <v-select :loading="loadingList" v-model="isoPath" :items="isoImages" v-if="!umount" append-icon="mdi-reload"
            variant="outlined" density="comfortable" @click:append="getIsoList">
            <template #no-data>
              <v-list-item :title="$t('dialogs.vmCdrom.noImages')"></v-list-item>
            </template>
          </v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" type="submit" :disabled="!umount && !isoPath">{{ $t('common.actions.submit') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script setup lang="ts">
import { apiClient } from '@/api'
import { hasAdminScope } from '@/composables/auth'
import type { schemas } from '@/composables/schemas'
import { useAuthStore } from '@/stores/auth'
import { ref, watch, type PropType } from 'vue'

const umount = ref(false)
const isoPath = ref<string>()

const isoImages = ref<string[]>([])
const loadingList = ref(false)
const auth = useAuthStore()

const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['DomainDetail']>,
    required: false,
  },
  target: String
})

async function submit() {
  if (!umount.value && !isoPath.value) return
  if (props.target) {

    if (props.item) {
      const res = await apiClient.PATCH("/api/tasks/vms/{uuid}/cdrom", {
        params: {
          path: { uuid: props.item.uuid },
          query: { admin: hasAdminScope(auth.scopes) },
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
  if (!model.value || !props.item) return
  loadingList.value = true
  isoImages.value = []
  try {
    const res = await apiClient.GET("/api/images", {
      params: {
        query: {
          admin: hasAdminScope(auth.scopes),
          limit: 0,
          nameLike: ".iso",
          nodeName: props.item.nodeName,
          projectId: hasAdminScope(auth.scopes) ? undefined : props.item.ownerProjectId,
        }
      }
    })
    if (res.data) {
      isoImages.value = res.data.data.map((d) => d.path)
    }
  } finally {
    loadingList.value = false
  }
}

watch(
  [model, () => props.item?.uuid, () => props.item?.nodeName, () => props.item?.ownerProjectId],
  ([open]) => {
    if (!open) return
    umount.value = false
    isoPath.value = undefined
    void getIsoList()
  },
  { immediate: true },
)

</script>
