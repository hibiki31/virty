<template>
  <div class="Login">
    <setup-virty-dialog ref="setupVirtyDialog" />
    <v-container class="d-flex justify-center align-center">
      <v-card class="elevation-3" min-width="450">
        <v-toolbar color="primary" dark>
          <v-toolbar-title>Login</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
        <v-form ref="form" v-model="isFormValid">
          <v-card-text>
            <v-text-field
              v-model="formData.username"
              :rules="[required]"
              label="Username"
              name="username"
              prepend-icon="mdi-account"
              required
              variant="underlined"
            ></v-text-field>

            <v-text-field
              v-model="formData.password"
              :rules="[required]"
              id="password"
              label="Password"
              name="password"
              prepend-icon="mdi-lock"
              required
              variant="underlined"
              type="password"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              v-if="apiVersion.initialized === false"
              v-on:click="this.openSetupVirtyDialog"
              depressed
              text
              color="primary"
              >Setup</v-btn
            >
            <v-btn
              @click.prevent="login"
              :disabled="!isFormValid"
              :loading="isLoadingLogin"
              depressed
              color="primary"
              type="submit"
              >Login</v-btn
            >
          </v-card-actions>
        </v-form>
      </v-card>
    </v-container>
  </div>
</template>

<script lang="ts" setup>
import axios from "@/axios";
import { AxiosError } from 'axios';
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { setAxios } from "@/composables/auth";
import { sleep } from "@/composables/mixins";
import { useNotification } from "@kyvg/vue3-notification";
import { useAuthStore } from "@/stores/auth";

// module load
const { notify } = useNotification();
const router = useRouter();
const auth = useAuthStore();

// form data
const formData = reactive({
  password: "",
  username: "",
});

// page state
const isLoadingLogin = ref(false);
const isFormValid = ref(false);

// server value
const accessToken = ref("");
const apiVersion = ref("");

// onMounted(async () => {});

const loadingLogin = async () => {
  await sleep(300);
  isLoadingLogin.value = false;
};

const required = (v: string): boolean => {
  return !!v?.length;
};

const login = async () => {
  isLoadingLogin.value = true;
  const params = new FormData();
  params.append("username", formData.username);
  params.append("password", formData.password);

  try {
    const res = await axios.post("/api/auth", params, {
      headers: { "content-type": "multipart/form-data" },
    });
    await loadingLogin();
    accessToken.value = res.data.access_token;
  } catch (error) {
    await loadingLogin();

    if (error instanceof AxiosError){
      notify({
      type: "error",
      title: "Error Returned from Server",
      text: error.response?.data.detail,
    });
    }
    return error;
  }

  notify({
    type: "success",
    title: "Login successful",
    text: "Redirecting to Home After Successful Login",
  });

  await setAxios(accessToken.value);
  await auth.loginSuccess(accessToken.value);

  router.push({ path: "/" });
};
</script>

<!--
<script>
import axios from "@/axios/index";
import SetupVirtyDialog from "@/components/dialog/SetupVirtyDialog.vue";
import { useNotification } from "@kyvg/vue3-notification";
const { notify } = useNotification();

import { setAxios } from '@/composables/auth'
import { useAuthStore } from '@/store/auth'
const auth = useAuthStore()

export default {
  name: "Login",
  props: {
    source: String,
  },
  components: {
    SetupVirtyDialog,
  },
  data: () => ({
    isFormValid: false,
    isLoadingLogin: false,
    formData: {
      userId: "",
      password: "",
    },
    apiVersion: {
      initialized: true,
    },
    rules: {
      required: (v) => !!v?.length,
    },
  }),
  methods: {
    openSetupVirtyDialog() {
      this.$refs.setupVirtyDialog.openDialog();
    },
    async doLogin() {
      this.isLoadingLogin = true;

      const params = new FormData();
      params.append("username", this.formData.userId);
      params.append("password", this.formData.password);
      await axios
        .post("/api/auth", params, {
          headers: {
            "content-type": "multipart/form-data",
          },
        })
        .then((res) => {
          notify({
            type: "success",
            title: "Login successful",
            text: "Redirecting to Home After Successful Login",
          });
          setAxios(accessToken.value)
          auth.loginSuccess(accessToken.value)

          // this.$store.dispatch("updateAuthState", res.data);
          // this.$_pushNotice("Login successful", "success");
          // this.$router.push(this.$route.query.redirect || { name: "VMList" });
        })
        .catch((error) => {
          notify({
            type: "error",
            title: "Error Returned from Server",
            text: error.response.data.detail,
          });
        });
      this.isLoadingLogin = false;
    },
  },
  mounted: async function () {
    await axios
      .get("/api/version")
      .then((response) => (this.apiVersion = response.data));
    if (!this.apiVersion.initialized) {
      this.$refs.setupVirtyDialog.openDialog();
    }
  },
};
</script> -->
