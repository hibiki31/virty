<template>
  <v-app>
    <v-main>
      <notifications position="right" width="290px" class="ma-10">
        <template #body="props">
          <v-alert
            :type="props.item.type"
            class="text-caption ma-2"
            density="compact"
            border="start"
            variant="text"
            elevation="1"
            ><v-alert-title class="text-subtitle-2">{{
              props.item.title
            }}</v-alert-title>
            {{ props.item.text }}
          </v-alert>
        </template>
      </notifications>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import axios from "@/axios";
import { AxiosError } from "axios";

import { onMounted } from "vue";
import { getCookie, removeCookie } from "typescript-cookie";
import { useRouter } from "vue-router";
import { useNotification } from "@kyvg/vue3-notification";
import { useAuthStore } from "@/stores/auth";
// module
const { notify } = useNotification();
const router = useRouter();
const auth = useAuthStore();

const authAPI = () => {
  const accessToken = getCookie("accessToken");

  if (!accessToken) {
    console.debug("token not found in cookie");
    router.push({ path: "/login" });
    auth.$state.tokenValidated = true;
    return;
  }

  axios
    .get("/api/auth/validate", {
      headers: {
        Authorization: "Bearer " + accessToken,
      },
    })
    .then(() => {
      axios.interceptors.request.use(
        (config) => {
          config.headers.Authorization = "Bearer " + accessToken;
          return config;
        },
        (err) => {
          return Promise.reject(err);
        }
      );
      notify({
        type: "success",
        title: "Login successful",
        text: "Redirecting to Home After Successful Login",
      });
      auth.loginSuccess(accessToken);
      router.push({ path: "/" });
    })
    .catch((error) => {
      if (error instanceof AxiosError) {
        notify({
          type: "error",
          title: "Error Returned from Server",
          text: error.response?.data.detail,
        });
        removeCookie("accessToken");
        auth.$state.tokenValidated = true;
        router.push({ path: "/login" });
      }
    });
};

onMounted(() => {
  console.debug("App.vue onMounted");
  authAPI();
});
</script>
