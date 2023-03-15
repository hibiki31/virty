import {
  Box,
  Divider,
  Drawer,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Select,
  Toolbar,
  Typography,
  useTheme,
} from '@mui/material';
import {
  Home,
  CubeOutline,
  CheckboxMultipleMarkedOutline,
  Server,
  Wan,
  Database,
  Harddisk,
  TagMultiple,
  Account,
  FolderStar,
} from 'mdi-material-ui';
import NextLink from 'next/link';
import { useRouter } from 'next/router';
import { FC, useEffect, useState } from 'react';
import { SCOPE_TO_LABEL } from '~/lib/api/auth';
import { useDrawer } from '~/store/drawerState';
import { useAuth } from '~/store/userState';

const drawerWidth = 250;
const drawerRoutes = [
  {
    title: 'Home',
    path: '/',
    icon: <Home />,
  },
  {
    title: 'VM',
    path: '/vm',
    icon: <CubeOutline />,
  },
  {
    title: 'Node',
    path: '/node',
    icon: <Server />,
  },
  {
    title: 'Network',
    path: '/network',
    icon: <Wan />,
  },
  {
    title: 'Storage',
    path: '/storage',
    icon: <Database />,
  },
  {
    title: 'Image',
    path: '/image',
    icon: <Harddisk />,
  },
  {
    title: 'Flavor',
    path: '/flavors',
    icon: <TagMultiple />,
  },
  {
    title: 'Users',
    path: '/users',
    icon: <Account />,
  },
  {
    title: 'Projects',
    path: '/projects',
    icon: <FolderStar />,
  },
  {
    title: 'Task',
    path: '/task',
    icon: <CheckboxMultipleMarkedOutline />,
  },
];

export const NavigationDrawer: FC = () => {
  const theme = useTheme();
  const { drawer } = useDrawer();
  const { user, changeScope } = useAuth();
  const router = useRouter();
  const [currentPath, setCurrentPath] = useState(router.pathname);

  useEffect(() => {
    setCurrentPath(router.pathname);
  }, [router]);

  return (
    <Drawer
      open={drawer}
      variant="persistent"
      sx={{
        ...(drawer
          ? {
              width: drawerWidth,
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
        ['& .MuiDrawer-paper']: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          {user?.username}
        </Typography>
        <FormControl fullWidth>
          <InputLabel id="scope-select-label">Scope</InputLabel>
          <Select
            labelId="scope-select-label"
            value={user?.scopeIndex}
            label="Scope"
            disabled={user?.scopes.length === 1}
            onChange={(e) => changeScope(e.target.value as number)}
          >
            {user?.scopes.map((scope, i) => (
              <MenuItem key={i} value={i}>
                {SCOPE_TO_LABEL[scope] || scope}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      <Divider />
      <List>
        {drawerRoutes.map((route, i) => (
          <ListItem
            key={i}
            dense
            disablePadding
            selected={currentPath === route.path}
            sx={{
              px: 1,
              py: 0.5,
              '> div': {
                borderRadius: 1,
              },
              '&.Mui-selected': {
                backgroundColor: theme.palette.background.default,
                '> div': {
                  backgroundColor: theme.palette.action.selected,
                },
              },
            }}
          >
            <NextLink href={{ pathname: route.path }}>
              <ListItemButton>
                <ListItemIcon>{route.icon}</ListItemIcon>
                <ListItemText primary={route.title} />
              </ListItemButton>
            </NextLink>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};
