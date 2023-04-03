import { Box, Divider, Drawer, IconButton, List, Toolbar, Typography, useTheme } from '@mui/material';
import { PageFirst } from 'mdi-material-ui';
import { useRouter } from 'next/router';
import { FC, memo, useMemo, useState } from 'react';
import { closedMixin, openedMixin } from '~/lib/utils/drawer';
import { useDrawer } from '~/store/drawerState';
import { DRAWER_ITEMS } from '../config';
import { DrawerListItem } from '../DrawerListItem';

export const SubNavigationDrawer: FC = memo(function NotMemoSubNavigationDrawer() {
  const theme = useTheme();
  const router = useRouter();
  const { leftDrawer, setLeftDrawer, toggleLeftDrawer } = useDrawer();
  const [open, setOpen] = useState(false);
  const [groupItem, drawerItems] = useMemo(() => {
    const group = router.pathname.split('/')[1];
    const groupItem = DRAWER_ITEMS.find((item) => item.path === `/${group}`);
    if (!groupItem?.children?.length) {
      return [null, []];
    }
    return [
      groupItem,
      groupItem.children.map((item) => ({
        ...item,
        path: `/${group}${item.path}`,
      })),
    ];
  }, [router.pathname]);

  return drawerItems.length ? (
    <Drawer
      open={leftDrawer || open}
      onClose={() => setLeftDrawer(false)}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      variant="permanent"
      sx={
        leftDrawer || open
          ? {
              ...openedMixin(theme),
              '& .MuiDrawer-paper': openedMixin(theme),
            }
          : {
              ...closedMixin(theme),
              '& .MuiDrawer-paper': closedMixin(theme),
              '& span': {
                opacity: 0,
              },
            }
      }
    >
      <Toolbar />
      <Box display="flex" alignItems="center" sx={{ px: 2, py: 1, gap: 2 }}>
        <IconButton disableRipple sx={{ pointerEvents: 'none' }}>
          {groupItem!.icon}
        </IconButton>
        <Typography variant="h6">{groupItem!.title}</Typography>
      </Box>
      <Divider />
      <List>
        {drawerItems.map((item, i) => (
          <DrawerListItem key={i} item={item} />
        ))}
      </List>
      <IconButton
        onClick={toggleLeftDrawer}
        sx={{
          position: 'absolute',
          bottom: theme.spacing(2),
          left: theme.spacing(2),
          transition: theme.transitions.create('transform', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          transform: leftDrawer ? 'rotate(0deg)' : 'rotate(180deg)',
        }}
      >
        <PageFirst />
      </IconButton>
    </Drawer>
  ) : null;
});
