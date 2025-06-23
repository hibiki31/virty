<template>
  <v-card :loading="loading ? 'white' : false" loa>
    <highlightjs :code="props.text || ''" :language='props.type' class="my-highlight"></highlightjs>
  </v-card>
</template>

<script lang="ts" setup>
const props = defineProps<{
  text: string | undefined | null,
  type: string,
  loading: boolean,
}>()
</script>

<style scoped>
.my-highlight :deep(.hljs) {
  font-size: 13px;
}
</style>
