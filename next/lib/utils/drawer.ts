import { CSSObject, Theme } from '@mui/material';

export const DRAWER_WIDTH = 250;

export const openedMixin = (theme: Theme, width: number | string = DRAWER_WIDTH): CSSObject => ({
  width,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.easeOut,
    duration: theme.transitions.duration.enteringScreen,
  }),
});

export const closedMixin = (theme: Theme, width: number | string = theme.spacing(9)): CSSObject => ({
  width: `calc(${width} + 1px)`,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
});
