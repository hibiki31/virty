<template>
  <v-dialog width="700" v-model="dialogState" data-testid="network-create-dialog" color="black">
    <v-form ref="formRef" @submit.prevent="submit">
      <v-card :title="t('dialogs.networkAdd.title')">
        <v-card-text>
          <!-- 基本 -->
          <v-row cols="12">
            <v-col>
              <v-text-field data-testid="network-name" variant="outlined" density="compact" :label="t('common.fields.name')" v-model="postData.name"
                :rules="[r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions]"
                counter="64"></v-text-field>
            </v-col>
            <v-col md="3">
              <v-select variant="outlined" density="compact" :label="t('common.fields.mode')" :items="itemsForwardMode"
                :rules="[r.required]" v-model="postData.forwardMode" @update:model-value="updateMode"></v-select>
            </v-col>
            <v-col md="3">
              <v-select variant="outlined" density="compact" :label="t('common.fields.node')" :items="itemsNodes.data" :rules="[r.required]"
                item-title="name" item-value="name" v-model="postData.nodeName"></v-select>
            </v-col>
            <v-col>
              <v-text-field variant="outlined" density="compact" :label="t('dialogs.networkAdd.bridgeName')" v-model="bridgeName"
                :rules="enableBridge ? [r.required, r.limitLength64, r.characterRestrictions, r.firstCharacterRestrictions] : []"
                counter="64"></v-text-field>
            </v-col>
          </v-row>

          <!-- Bridge Name -->


          <v-divider></v-divider>
          <p class="text-body-2 pt-3">
            {{ t('dialogs.networkAdd.gatewayHelp') }}</p>


          <v-row class="pt-1">
            <!-- IP -->
            <v-col>
              <v-checkbox density="compact" :label="t('dialogs.networkAdd.enableGateway')" color="primary" hide-details v-model="enableIP"
                :disabled="disableIP"
                @update:model-value="() => { if (!enableIP) { enableDHCP = false } }"></v-checkbox>
              <v-row cols="12">
                <v-col>
                  <v-text-field variant="outlined" density="compact" :label="t('dialogs.networkAdd.ip')" v-model="postDataIP.address"
                    :disabled="!enableIP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field variant="outlined" density="compact" :label="t('dialogs.networkAdd.netmask')" v-model="postDataIP.netmask"
                    :disabled="!enableIP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <!-- DHCP -->
            <v-col>
              <v-checkbox density="compact" :label="t('dialogs.networkAdd.enableDhcp')" color="primary" hide-details v-model="enableDHCP"
                :disabled="disableIP || !enableIP"></v-checkbox>
              <v-row cols="12">
                <v-col>
                  <v-text-field variant="outlined" density="compact" :label="t('dialogs.networkAdd.start')" v-model="postDataDHCP.start"
                    :disabled="!enableDHCP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field variant="outlined" density="compact" :label="t('dialogs.networkAdd.end')" v-model="postDataDHCP.end"
                    :disabled="!enableDHCP" :rules="[r.required, r.isValidIp]" counter="64"></v-text-field>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn data-testid="network-create-cancel" variant="text" @click="dialogState = false">{{ t('common.actions.cancel') }}</v-btn>
          <v-btn data-testid="network-create-submit" color="primary" type="submit" :loading="loading">{{ t('common.actions.create') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>

</template>

<script lang="ts" setup>
import type { schemas } from '@/composables/schemas';
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useLocalizedRules } from '@/composables/rules';

import { getNode } from '@/composables/nodes';
import { apiClient } from '@/api';
import notify, { apiErrorRef, notifyTask } from '@/composables/notify';
import { translationRef } from '@/composables/i18n';

const dialogState = defineModel({ default: false })
const { t } = useI18n({ useScope: 'global' })
const r = useLocalizedRules()
const loading = ref(false)

const disableIP = ref(false)
const enableIP = ref(true)
const enableDHCP = ref(true)
const bridgeName = ref("")
const enableBridge = ref(false)

const itemsForwardMode = computed(() => [
  { title: t('common.fields.bridge'), value: "bridge" },
  { title: "NAT", value: "nat" },
  { title: "OVS", value: "ovs" },
  { title: t('dialogs.networkAdd.route'), value: "route" },
  { title: t('dialogs.networkAdd.isolated'), value: "isolated" },
])

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
  if (value === 'isolated' || value === 'ovs') {
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

  if (enableBridge.value) {
    postData.bridgeName = bridgeName.value
  } else {
    postData.bridgeName = undefined
  }

  try {
    const res = await apiClient.POST('/api/tasks/networks', { body: postData })
    if (res.data) {
      notifyTask(res.data[0].uuid)
      dialogState.value = false
    } else if (res.error) {
      notify('error', translationRef('dialogs.networkAdd.createFailed'), apiErrorRef(res.error))
    }
  } catch {
    notify('error', translationRef('dialogs.networkAdd.createFailed'), translationRef('dialogs.networkAdd.unreachable'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  itemsNodes.value = await getNode()
})

</script>
