import { FC, PropsWithChildren, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Select,
  Toolbar,
  Typography,
} from '@mui/material';
import { useAuth } from '~/store/userState';
import { Menu as MdiMenu, Account, Cog, Logout } from 'mdi-material-ui';
import { NavigationDrawer } from './NavigationDrawer';
import { SubNavigationDrawer } from './NavigationDrawer/SubNavigationDrawer';
import { SCOPE_TO_LABEL } from '~/lib/api/auth';
import { useIncompleteTasks } from '~/store/tasksState';
import { IncompleteTasksButton } from './IncompleteTasksButton';

export const DefaultHeader: FC<PropsWithChildren> = ({ children }) => {
  const [userMenuAnchorEl, setUserMenuAnchorEl] = useState<null | HTMLElement>(null);
  const isUserMenuOpen = Boolean(userMenuAnchorEl);
  const { user, logout, changeScope } = useAuth();
  const [open, setOpen] = useState(false);
  const { count } = useIncompleteTasks();

  const openUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchorEl(event.currentTarget);
  };

  const closeUserMenu = () => {
    setUserMenuAnchorEl(null);
  };

  return (
    <>
      <AppBar color="inherit" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: 'primary.main' }}>
        <Toolbar variant="dense">
          <IconButton edge="start" color="inherit" sx={{ mr: 2 }} onClick={() => setOpen(!open)}>
            <MdiMenu />
          </IconButton>
          <Typography variant="h5" mr={4}>
            Virty
          </Typography>
          {children ? children : <Box component="div" sx={{ mr: 'auto' }} />}
          <IncompleteTasksButton count={count} />
          <Box component="div" sx={{ display: 'flex', alignItems: 'center' }}>
            <Button variant="outlined" color="inherit" sx={{ borderRadius: 5 }} onClick={openUserMenu}>
              <Account sx={{ mr: 0.5 }} />
              <Cog />
            </Button>
          </Box>

          <Menu
            anchorEl={userMenuAnchorEl}
            open={isUserMenuOpen}
            onClose={closeUserMenu}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            sx={{ mt: 1, '& .MuiPaper-root': { minWidth: 250 } }}
          >
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
            <Divider sx={{ my: 1 }} />
            <MenuItem>
              <ListItemIcon>
                <Cog fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </MenuItem>
            <MenuItem onClick={logout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <NavigationDrawer open={open} onClose={() => setOpen(false)} />
      <SubNavigationDrawer />
    </>
  );
};
