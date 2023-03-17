import { Drawer, List, Toolbar, useTheme } from '@mui/material';
import { FC, memo } from 'react';
import { DRAWER_ITEMS, DRAWER_WIDTH } from './config';
import { DrawerListItem } from './DrawerListItem';

type Props = {
  open: boolean;
  onClose: () => void;
};

export const NavigationDrawer: FC<Props> = memo(function NotMemoNavigationDrawer({ open, onClose }) {
  const theme = useTheme();

  return (
    <Drawer
      open={open}
      onClose={onClose}
      sx={{
        ...(open
          ? {
              width: DRAWER_WIDTH,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.easeOut,
                duration: theme.transitions.duration.enteringScreen,
              }),
            }
          : {
              width: 0,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
              }),
            }),
        ['& .MuiDrawer-paper']: { width: DRAWER_WIDTH, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List>
        {DRAWER_ITEMS.map((item, i) => (
          <DrawerListItem key={i} item={item} />
        ))}
      </List>
    </Drawer>
  );
});
