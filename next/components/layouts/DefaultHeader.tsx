import { FC, PropsWithChildren, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Divider,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '~/store/userState';
import { useDrawer } from '~/store/drawerState';

export const DefaultHeader: FC<PropsWithChildren> = ({ children }) => {
  const [userMenuAnchorEl, setUserMenuAnchorEl] = useState<null | HTMLElement>(null);
  const isUserMenuOpen = Boolean(userMenuAnchorEl);
  const { user, logout } = useAuth();
  const { toggleDrawer } = useDrawer();

  const openUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchorEl(event.currentTarget);
  };

  const closeUserMenu = () => {
    setUserMenuAnchorEl(null);
  };

  return (
    <AppBar color="inherit" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: 'primary.main' }}>
      <Toolbar>
        <IconButton size="large" edge="start" color="inherit" sx={{ mr: 2 }} onClick={toggleDrawer}>
          <MenuIcon />
        </IconButton>
        <Typography variant="h5" mr={4}>
          Virty
        </Typography>
        {children ? children : <Box component="div" sx={{ mr: 'auto' }} />}
        <Box component="div" sx={{ display: 'flex', alignItems: 'center' }}>
          <Button variant="outlined" color="inherit" sx={{ borderRadius: 5 }} onClick={openUserMenu}>
            <PersonIcon sx={{ mr: 0.5 }} />
            <SettingsIcon />
          </Button>
        </Box>

        <Menu
          anchorEl={userMenuAnchorEl}
          open={isUserMenuOpen}
          onClose={closeUserMenu}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          sx={{ mt: 1, '& .MuiPaper-root': { minWidth: 200 } }}
        >
          <Box component="div" sx={{ px: 2 }}>
            <ListItemText primary={user?.username} />
          </Box>
          <Divider sx={{ my: 1 }} />
          <MenuItem>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </MenuItem>
          <MenuItem onClick={logout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};
