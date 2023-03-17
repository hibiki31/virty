import {
  Box,
  Divider,
  Drawer,
  FormControl,
  InputLabel,
  List,
  MenuItem,
  Select,
  Toolbar,
  Typography,
  useTheme,
} from '@mui/material';
import { FC, memo } from 'react';
import { SCOPE_TO_LABEL } from '~/lib/api/auth';
import { useDrawer } from '~/store/drawerState';
import { useAuth } from '~/store/userState';
import { DRAWER_ITEMS, DRAWER_WIDTH } from './config';
import { DrawerListItem } from './DrawerListItem';

export const NavigationDrawer: FC = memo(function NotMemoNavigationDrawer() {
  const theme = useTheme();
  const { drawer } = useDrawer();
  const { user, changeScope } = useAuth();

  return (
    <Drawer
      open={drawer}
      variant="persistent"
      sx={{
        ...(drawer
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
        {DRAWER_ITEMS.map((item, i) => (
          <DrawerListItem key={i} item={item} />
        ))}
      </List>
    </Drawer>
  );
});
