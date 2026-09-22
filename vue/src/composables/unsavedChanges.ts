import { onBeforeUnmount, onMounted, type Ref } from 'vue';
import { onBeforeRouteLeave } from 'vue-router';
import { useI18n } from 'vue-i18n';

export function useUnsavedChanges(dirty: Ref<boolean>, busy: Ref<boolean>) {
  const { t } = useI18n({ useScope: 'global' });
  const confirmDiscard = () => !busy.value && (!dirty.value || window.confirm(t('userManagement.discard')));
  let leaving = false;
  function beforeLogout(event: Event) {
    if (!confirmDiscard()) event.preventDefault();
    else leaving = true;
  }
  function beforeUnload(event: BeforeUnloadEvent) {
    if (leaving || (!dirty.value && !busy.value)) return;
    event.preventDefault();
    event.returnValue = '';
  }
  onMounted(() => {
    window.addEventListener('beforeunload', beforeUnload);
    window.addEventListener('virty:before-logout', beforeLogout);
    window.addEventListener('virty:before-mode-change', beforeLogout);
  });
  onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', beforeUnload);
    window.removeEventListener('virty:before-logout', beforeLogout);
    window.removeEventListener('virty:before-mode-change', beforeLogout);
  });
  onBeforeRouteLeave(confirmDiscard);
  return { confirmDiscard };
}
