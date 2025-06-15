import { defineStore } from "pinia";
import { ref } from "vue";

export const useStateStore = defineStore("state", () => {
  const pageIndex = ref(1);
  const showSideDrawer = ref(true);
  const reloadTrigger = ref(false);

  function trigger() {
    reloadTrigger.value = true;
    setTimeout(() => (reloadTrigger.value = false), 0);
  }

  return { pageIndex, showSideDrawer, reloadTrigger, trigger };
});
