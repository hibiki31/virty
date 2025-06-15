<template>
  <v-footer app height="25">
    <div class="text-caption text-disabled" style="position: absolute; right: 16px;">
      &copy; 2019-{{ (new Date()).getFullYear() }} <span class="d-none d-sm-inline-block">hibiki31</span>
      —
      <a class="text-decoration-none on-surface" rel="noopener noreferrer" target="_blank">
        v{{ version }}
      </a>
    </div>
  </v-footer>
</template>

<script setup lang="ts">
const version = import.meta.env.VITE_APP_VERSION
</script>
