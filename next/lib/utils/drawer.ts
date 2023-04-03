import { CSSObject, Theme } from '@mui/material';

export const DRAWER_WIDTH = 250;

export const opendMixin = (theme: Theme, width: number = DRAWER_WIDTH): CSSObject => ({
  width,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.easeOut,
    duration: theme.transitions.duration.enteringScreen,
  }),
});

export const closedMixin = (theme: Theme): CSSObject => ({
  width: `calc(${theme.spacing(9)} + 1px)`,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
});
