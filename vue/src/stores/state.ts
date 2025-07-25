import { defineStore } from "pinia";
import { ref } from "vue";

export const useStateStore = defineStore("state", () => {
  const pageIndex = ref(1);
  const showSideDrawer = ref<boolean | undefined>(undefined);
  const reloadTrigger = ref(false);
  const task_uuids = ref<string[]>([]);

  function trigger() {
    reloadTrigger.value = true;
    setTimeout(() => (reloadTrigger.value = false), 0);
  }

  return { pageIndex, showSideDrawer, reloadTrigger, task_uuids, trigger };
});
