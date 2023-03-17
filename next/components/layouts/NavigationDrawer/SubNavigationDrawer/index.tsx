import { Box, CSSObject, Divider, Drawer, IconButton, List, Theme, Toolbar, Typography, useTheme } from '@mui/material';
import { PageFirst } from 'mdi-material-ui';
import { useRouter } from 'next/router';
import { FC, memo, useMemo, useState } from 'react';
import { useDrawer } from '~/store/drawerState';
import { DRAWER_ITEMS, DRAWER_WIDTH } from '../config';
import { DrawerListItem } from '../DrawerListItem';

const opendMixin = (theme: Theme): CSSObject => ({
  width: DRAWER_WIDTH,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.easeOut,
    duration: theme.transitions.duration.enteringScreen,
  }),
});

const closedMixin = (theme: Theme): CSSObject => ({
  width: `calc(${theme.spacing(9)} + 1px)`,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
});

export const SubNavigationDrawer: FC = memo(function NotMemoSubNavigationDrawer() {
  const theme = useTheme();
  const router = useRouter();
  const { drawer, closeDrawer, toggleDrawer } = useDrawer();
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
      open={drawer || open}
      onClose={closeDrawer}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      variant="permanent"
      sx={
        drawer || open
          ? {
              ...opendMixin(theme),
              '& .MuiDrawer-paper': opendMixin(theme),
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
        onClick={toggleDrawer}
        sx={{
          position: 'absolute',
          bottom: theme.spacing(2),
          left: theme.spacing(2),
          transition: theme.transitions.create('transform', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          transform: drawer ? 'rotate(0deg)' : 'rotate(180deg)',
        }}
      >
        <PageFirst />
      </IconButton>
    </Drawer>
  ) : null;
});
