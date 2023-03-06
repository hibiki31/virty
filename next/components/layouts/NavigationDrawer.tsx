import {
  Card,
  CardContent,
  CardHeader,
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
  useTheme,
} from '@mui/material';
import { Home, CubeOutline } from 'mdi-material-ui';
import NextLink from 'next/link';
import { useRouter } from 'next/router';
import { FC, useEffect, useState } from 'react';
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
];

export const NavigationDrawer: FC = () => {
  const theme = useTheme();
  const { drawer } = useDrawer();
  const { user } = useAuth();
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
      <Card>
        <CardHeader title={user?.username} />
        <CardContent>
          <FormControl fullWidth>
            <InputLabel id="scope-select-label">Scope</InputLabel>
            <Select
              labelId="scope-select-label"
              value={'admin'}
              label="Scope"
              // onChange={handleChange}
            >
              {user?.scopes.map((scope, i) => (
                <MenuItem key={i} value={scope}>
                  {scope}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </CardContent>
      </Card>
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
