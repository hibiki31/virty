<template>
  <v-card :loading="loading ? 'white' : false" loa>
    <highlightjs :code="props.text || ''" :language="props.type"></highlightjs>
  </v-card>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue';

const props = defineProps<{
  text: string | undefined,
  type: string,
  loading: boolean
}>()


</script>
