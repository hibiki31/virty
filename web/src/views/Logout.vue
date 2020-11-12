<template>
  <div class="logout">
    Logout....
  </div>
</template>

<script>
// @ is an alias to /src

export default {
  name: 'Logout',
  async mounted() {
    await this.$_sleep(1000);
    this.$store.dispatch('updateAuthState', {});
    this.$router.push({ name: 'Login' });
  }
};
</script>
