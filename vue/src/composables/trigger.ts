import { watch } from "vue";
import { useStateStore } from "@/stores/state";

export function useReloadListener(onTrigger: () => void) {
  const state = useStateStore();

  watch(
    () => state.reloadTrigger,
    (val) => {
      if (val) {
        onTrigger();
      }
    }
  );
}
