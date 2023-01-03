import { OptionsObject, SnackbarKey, useSnackbar } from 'notistack';
import { useEffect, useState } from 'react';

export const useNotistack = () => {
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();
  const [isExited, setIsExited] = useState(true);
  const [enqueueArgs, setEnqueueArgs] = useState<{
    message: string;
    options?: OptionsObject;
  }>();
  const [snackbarKey, setSnackbarKey] = useState<SnackbarKey>();

  const openPersistNotistack = (message: string, options?: OptionsObject): void => {
    closePersistNotistack();
    setEnqueueArgs({ message, options });
  };
  // enqueueSnackbar when notistack is exited
  useEffect(() => {
    if (isExited && enqueueArgs) {
      const { message, options } = enqueueArgs;
      const key = enqueueSnackbar(message, {
        persist: true,
        anchorOrigin: { vertical: 'bottom', horizontal: 'center' },
        ...options,
        onExited: () => {
          setIsExited(true);
        },
      });
      setSnackbarKey(key);
      setIsExited(false);
    }
  }, [isExited, enqueueArgs, enqueueSnackbar]);

  const closePersistNotistack = (): void => {
    setSnackbarKey(undefined);
  };
  // closeSnackbar when snackbarKey is changed or unmounted
  useEffect(() => {
    return () => {
      if (snackbarKey) {
        closeSnackbar(snackbarKey);
      }
    };
  }, [snackbarKey, closeSnackbar]);

  return { enqueueNotistack: enqueueSnackbar, openPersistNotistack, closePersistNotistack };
};
