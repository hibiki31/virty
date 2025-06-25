<template>
  <v-dialog width="400" v-model="model">
    <v-card>
      <v-form ref="formRef" @submit.prevent="submit">
        <v-card-title>Network Change</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="12">
              <v-select variant="outlined" density="comfortable" :items="itemsNetworks?.data" item-title="name"
                hide-details item-value="uuid" :rules="[r.required]" v-model="networkUuid" label="Network"></v-select>
            </v-col>
            <v-col cols="12" md="12" v-if="checkOVS()">
              <v-select variant="outlined" density="comfortable" :items="itemsPort()" hide-details :rules="[r.required]"
                v-model="networkPort" label="Port"></v-select>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn :loading="loadingSubmit" color="primary" type="submit">Change</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { apiClient } from '@/api'
import type { schemas } from '@/composables/schemas'
import type { typeListNetwork } from '@/composables/network'

// Form
const networkUuid = ref<string>()
const networkPort = ref<string>()

// State
const loadingSubmit = ref(false)
const loadingList = ref(false)

// Model Props
const model = defineModel({ default: false })
const props = defineProps({
  item: {
    type: Object as PropType<schemas['DomainDetail']>,
    required: false,
  },
  mac: String
})

const itemsNetworks = ref<typeListNetwork>()

async function submit() {
  if (!(props.mac && props.item && networkUuid.value)) {
    return
  }
  if (!checkOVS()) {
    networkPort.value = undefined
  }

  const res = await apiClient.PATCH("/api/tasks/vms/{uuid}/network", {
    params: {
      path: { uuid: props.item.uuid }
    },
    body: {
      mac: props.mac,
      networkUuid: networkUuid.value,
      port: networkPort.value,
    }
  })
  if (res.data) {
    model.value = false
  }
}

function checkOVS(): boolean {
  if (itemsNetworks.value && networkUuid) {
    const net = itemsNetworks.value.data
      .filter(n => n.uuid === networkUuid.value)

    if (net.length === 1) {
      return net[0].type === 'openvswitch'
    } else {
      return false
    }
  } else { return false }
}

function itemsPort() {
  if (!networkUuid.value) return [];
  if (!itemsNetworks.value) return [];

  const net = itemsNetworks.value.data.find(n => n.uuid === networkUuid.value)
  if (!net) return [];

  return net.portgroups.map(p => ({
    title: `${p.name} (${p.vlanId})`,
    value: p.name,
  })) ?? [];
}

async function getNetworkList() {
  loadingList.value = true
  if (model && props.item) {
    const res = await apiClient.GET("/api/networks", {
      params: {
        query: {
          admin: true,
          nodeNameLike: props.item.nodeName
        }
      }
    })
    if (res.data) {
      itemsNetworks.value = res.data
    }
  }
  loadingList.value = false
}

onMounted(() => {
  getNetworkList()
})

</script>
