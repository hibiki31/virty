<template>
  <v-dialog width="700" v-model="dialogState" color="black">
    <v-form ref="formRef" @submit.prevent="submit">
      <v-card title="Create Network">
        <v-card-text>
          <!-- 基本 -->
          <v-row cols="12">
            <v-col>
              <v-text-field variant="outlined" density="compact" label="Name" v-model="postData.name"
                :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                counter="64"></v-text-field>
            </v-col>
            <v-col md="3">
              <v-select variant="outlined" density="compact" label="Mode" :items="itemsForwardMode"
                :rules="[r.required]" v-model="postData.forwardMode" @update:model-value="updateMode"></v-select>
            </v-col>
            <v-col md="3">
              <v-select variant="outlined" density="compact" label="Node" :items="itemsNodes.data" :rules="[r.required]"
                item-title="name" item-value="name" v-model="postData.nodeName"></v-select>
            </v-col>
            <v-col>
              <v-text-field variant="outlined" density="compact" label="Bridge Name" v-model="bridgeName"
                :disabled="!enableBridge"
                :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                counter="64"></v-text-field>
            </v-col>
          </v-row>

          <!-- Bridge Name -->


          <v-divider></v-divider>
          <p class="text-body-2 pt-3">
            The GW is not available for type isolated, ovs. DHCP must be enabled on the GW.</p>


          <v-row class="pt-1">
            <!-- IP -->
            <v-col>
              <v-checkbox density="compact" label="Enable GW" color="primary" hide-details v-model="enableIP"
                :disabled="disableIP"
                @update:model-value="() => { if (!enableIP) { enableDHCP = false } }"></v-checkbox>
              <v-row cols="12">
                <v-col>
                  <v-text-field variant="outlined" density="compact" label="IP" v-model="postDataIP.address"
                    :disabled="!enableIP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field variant="outlined" density="compact" label="Netmask" v-model="postDataIP.netmask"
                    :disabled="!enableIP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <!-- DHCP -->
            <v-col>
              <v-checkbox density="compact" label="Enable DHCP" color="primary" hide-details v-model="enableDHCP"
                :disabled="disableIP || !enableIP"></v-checkbox>
              <v-row cols="12">
                <v-col>
                  <v-text-field variant="outlined" density="compact" label="Start" v-model="postDataDHCP.start"
                    :disabled="!enableDHCP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field variant="outlined" density="compact" label="End" v-model="postDataDHCP.end"
                    :disabled="!enableDHCP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="primary" type="submit" :loading="loading">CREATE</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>

</template>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas';

import { getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import { notifyTask } from '@/composables/notify';
import { asyncSleep } from '@/composables/sleep';

const dialogState = defineModel({ default: false })
const loading = ref(false)

const disableIP = ref(false)
const enableIP = ref(true)
const enableDHCP = ref(true)
const bridgeName = ref("")
const enableBridge = ref(false)

const itemsForwardMode = [
  { title: "Bridge", value: "bridge" },
  { title: "NAT", value: "nat" },
  { title: "OVS", value: "ovs" },
  { title: "Route", value: "route" },
  { title: "Isorated", value: "isorated" },
]

const itemsNodes = ref<schemas["NodePage"]>({ count: 0, data: [], })

const postDataIP = reactive<NonNullable<schemas["NetworkForCreate"]["ip"]>>({
  address: '192.168.0.254',
  netmask: '255.255.255.0'
})
const postDataDHCP = reactive<NonNullable<schemas["NetworkForCreate"]["dhcp"]>>({
  start: '192.168.0.1',
  end: '192.168.0.200'
})
const postData = reactive<schemas["NetworkForCreate"]>({
  name: '',
  nodeName: '',
  description: '',
  forwardMode: 'nat',
  dhcp: undefined,
  ip: undefined,
  bridgeName: undefined
})

function updateMode(value: string) {

  // IPを使用しないケース
  if (value === 'isorated' || value === 'ovs') {
    enableIP.value = false;
    enableDHCP.value = false;
    disableIP.value = true
  } else {
    disableIP.value = false
  }

  // ブリッジ名が必要なケース
  if (value === 'bridge' || value === 'ovs') {
    enableBridge.value = true
  } else {
    enableBridge.value = false
  }
}


async function submit(event: Promise<{ valid: boolean }>) {
  if (!(await event).valid) {
    return
  }

  loading.value = true

  if (enableIP.value) {
    postData.ip = postDataIP
    if (enableDHCP.value) {
      postData.dhcp = postDataDHCP
    } else {
      postData.dhcp = undefined
    }
  } else {
    postData.ip = undefined
    postData.dhcp = undefined
  }

  if (enableBridge) {
    postData.bridgeName = bridgeName.value
  }

  const res = await apiClient.POST('/api/tasks/networks', { body: postData })
  asyncSleep(500)
  if (res.data) {
    notifyTask(res.data[0].uuid)
    dialogState.value = false
  }
  loading.value = false
}

onMounted(async () => {
  itemsNodes.value = await getNode()
})

</script>
