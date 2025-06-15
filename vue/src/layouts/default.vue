<template>
  <v-main>
    <div>
      <MainAppBer></MainAppBer>
      <MainNavigation />
      <router-view class="ma-4" />
      <AppFooter />
    </div>
  </v-main>

</template>

<script lang="ts" setup>
console.log("default")
</script>
