<template>
  <v-main>
    <div>
      <MainAppBer></MainAppBer>
      <MainNavigation />
      <router-view class="ma-4" />
    </div>
  </v-main>
  <!-- <AppFooter /> -->
</template>

<script lang="ts" setup>
console.log("default")
</script>
