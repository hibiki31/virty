import { useMediaQuery, useTheme } from '@mui/material';
import { useCallback, useEffect } from 'react';
import { atom, useRecoilState } from 'recoil';

export const leftDrawerState = atom<boolean>({
  key: 'leftDrawer',
  default: true,
});

export const rightDrawerState = atom<boolean>({
  key: 'rightDrawer',
  default: true,
});

type DrawerOptions = {
  enable?: boolean;
  openedWidth?: string;
  closedWidth?: string;
};

export const rightDrawerOptionsState = atom<DrawerOptions>({
  key: 'rightDrawerOptions',
  default: {
    enable: false,
  },
});

export const useDrawer = () => {
  const theme = useTheme();
  const isMediumScreen = useMediaQuery(theme.breakpoints.down('md'));
  const [leftDrawer, setLeftDrawer] = useRecoilState(leftDrawerState);
  const [rightDrawer, setRightDrawer] = useRecoilState(rightDrawerState);
  const [rightDrawerOptions, _setRightDrawerOptions] = useRecoilState(rightDrawerOptionsState);

  useEffect(() => {
    if (isMediumScreen) {
      setRightDrawer(false);
    } else {
      setRightDrawer(true);
    }
  }, [isMediumScreen, setRightDrawer]);

  const toggleLeftDrawer = useCallback(() => {
    setLeftDrawer((prev) => !prev);
  }, [setLeftDrawer]);

  const toggleRightDrawer = useCallback(() => {
    setRightDrawer((prev) => !prev);
  }, [setRightDrawer]);

  const setRightDrawerOptions = useCallback(
    (options: DrawerOptions) => {
      _setRightDrawerOptions((prev) => ({
        ...prev,
        ...options,
      }));
    },
    [_setRightDrawerOptions]
  );

  const resetRightDrawer = useCallback(() => {
    setRightDrawer(true);
    _setRightDrawerOptions({
      enable: false,
    });
  }, [setRightDrawer, _setRightDrawerOptions]);

  return {
    leftDrawer,
    setLeftDrawer,
    toggleLeftDrawer,
    rightDrawer: rightDrawerOptions.enable ? rightDrawer : false,
    setRightDrawer,
    toggleRightDrawer,
    rightDrawerOptions,
    setRightDrawerOptions,
    resetRightDrawer,
  };
};
