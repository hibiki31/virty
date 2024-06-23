<script setup lang="ts">
import getHeader from "@/composables/auth.ts"


const { data: dataVersion } = await useVirty("/api/version")

const head = await getHeader()

const { data: dataVm } = await useVirty("/api/vms", {
  method: "GET",
  headers: head
}) 


const { data: dataNode } = await useVirty("/api/nodes", {
  method: "GET",
  headers: head,
  query: {
    nameLike:"w"
  }
}) 




</script>
<template>
  <div>
    {{ dataVersion }}
    {{ dataVm }}
    {{ dataNode }}
  </div>
</template>