<template>
  <div class="Login">
    <setup-virty-dialog ref="setupVirtyDialog"/>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card v-if="$route.query.redirect && !$_userData.isLoaded" flat>
            <v-card-text class="text-center">
              <div class="body-1 mb-3">Now loading...</div>
              <v-progress-circular indeterminate color="primary" />
            </v-card-text>
          </v-card>
          <v-card v-else class="elevation-12">
            <v-toolbar color="primary" dark>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-form ref="form" v-model="isFormValid">
              <v-card-text>
                <v-text-field
                  v-model="formData.userId"
                  :rules="[rules.required]"
                  label="userId"
                  name="userId"
                  prepend-icon="mdi-account"
                  required
                  type="text"
                ></v-text-field>

                <v-text-field
                  v-model="formData.password"
                  :rules="[rules.required]"
                  id="password"
                  label="Password"
                  name="password"
                  prepend-icon="mdi-lock"
                  required
                  type="password"
                ></v-text-field>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  v-on:click="this.openSetupVirtyDialog"
                  depressed
                  text
                  color="secondary"
                >Setup</v-btn>
                <v-btn
                  @click.prevent="doLogin"
                  :disabled="!isFormValid"
                  :loading="isLoadingLogin"
                  depressed
                  color="primary"
                  type="submit"
                >Login</v-btn>
              </v-card-actions>
            </v-form>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style lang="scss">
.Login {
  > * {
    margin: auto;
  }
}
</style>

<script>
import axios from '@/axios/index';
import SetupVirtyDialog from '../conponents/dialog/SetupVirtyDialog.vue';

export default {
  name: 'Login',
  props: {
    source: String
  },
  components: {
    SetupVirtyDialog
  },
  data: () => ({
    isFormValid: false,
    isLoadingLogin: false,
    formData: {
      userId: '',
      password: ''
    },
    rules: {
      required: (v) => !!v?.length
    }
  }),
  methods: {
    openSetupVirtyDialog() {
      this.$refs.setupVirtyDialog.openDialog();
    },
    async doLogin() {
      this.isLoadingLogin = true;

      const params = new FormData();
      params.append('username', this.formData.userId);
      params.append('password', this.formData.password);
      await axios
        .post(
          '/api/auth',
          params,
          {
            headers: {
              'content-type': 'multipart/form-data'
            }
          }
        )
        .then((res) => {
          if (res.status === 401) {
            this.$_pushNotice('Wrong userID or password', 'error');
          } else if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$store.dispatch('updateAuthState', res.data);
          this.$_pushNotice('Login success', 'success');
          this.$router.push({ name: 'VMList' });
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error');
        });
      this.isLoadingLogin = false;
    }
  }
};
</script>
