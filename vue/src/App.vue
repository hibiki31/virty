<template>
  <notifications position="bottom right" width="290px">
    <template #body="props">
      <v-alert :type="props.item.type" class="text-caption ma-1" density="compact" border="start" variant="text"
        style="background-color: white"><v-alert-title class="text-subtitle-2">{{ props.item.title }}</v-alert-title>
        {{ props.item.text }}
      </v-alert>
    </template>
  </notifications>
  <v-app>
    <router-view />
  </v-app>
</template>

<script lang="ts" setup>
//
</script>
