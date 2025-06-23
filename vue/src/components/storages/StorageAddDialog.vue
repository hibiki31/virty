<template>
  <v-dialog width="400" v-model="dialogState">
    <v-card>
      <v-form @submit.prevent="submit">
        <v-card-title>Register Storage</v-card-title>
        <v-card-text>
          <div class="mb-5">
            Please create the folder on the host first. <br>
            Basically 3 are needed, one for vm image, one for cloud-init, and one for iso image.
            Assign roles to each storage after adding.
          </div>
          <v-text-field variant="outlined" density="comfortable" label="Display name on virty" v-model="postData.name"
            :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]" counter="64"
            class="mb-3"></v-text-field>
          <v-select variant="outlined" density="comfortable" label="Select node name" :items="itemsNodes.data"
            class="mb-3" item-title="name" item-value="name" v-model="postData.nodeName" :rules="[r.required]">
          </v-select>
          <v-text-field variant="outlined" density="comfortable" label="Path" v-model="postData.path"
            :rules="[r.required]" counter="128" class="mb-3"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" type="submit">ADD</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { ref, defineModel, onMounted, defineProps } from 'vue';
import type { typeListNode } from '@/composables/nodes';
import { initNodeList, getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import { notifyTask } from '@/composables/notify';
import * as r from '@/composables/rules';

const dialogState = defineModel({ default: false })

const itemsNodes = ref<typeListNode>(initNodeList)
const postData = reactive({
  name: '',
  path: '',
  nodeName: ''
})

async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }
  apiClient.POST('/api/tasks/storages', { body: postData }).then((res) => {
    if (res.data) {
      notifyTask(res.data[0].uuid || "")
    }
  })
}


onMounted(async () => {
  itemsNodes.value = await getNode()
})
</script>
