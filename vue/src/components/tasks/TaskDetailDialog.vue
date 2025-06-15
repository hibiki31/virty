<template>
  <v-dialog v-model="model" width="auto">
    <v-card max-width="400" prepend-icon="mdi-update" :text="text" :title="title">
      <template v-slot:actions>
        <v-btn class="ms-auto" text="Ok" @click="model = false"></v-btn>
      </template>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, defineModel } from 'vue'

const model = defineModel({ default: false })

defineProps(['title', 'text'])

</script>
