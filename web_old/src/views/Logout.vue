<template>
  <div class="logout">
    Logout....
  </div>
</template>

<script>

export default {
  name: 'Logout',
  async mounted() {
    await this.$_sleep(1000);
    this.$store.dispatch('updateAuthState', {});
    this.$router.push({ name: 'Login' });
  }
};
</script>
