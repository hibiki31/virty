import { Box, Divider, Drawer, IconButton, Toolbar, Typography, useTheme } from '@mui/material';
import { FilterSettings } from 'mdi-material-ui';
import { FC, useEffect } from 'react';
import { closedMixin, openedMixin } from '~/lib/utils/drawer';
import { useDrawer } from '~/store/drawerState';

const DRAWER_WIDTH = 350;

export const FilterSettingsDrawer: FC = () => {
  const { rightDrawer, setRightDrawer, toggleRightDrawer, setRightDrawerOptions, resetRightDrawer } = useDrawer();
  const theme = useTheme();

  useEffect(() => {
    setRightDrawerOptions({
      enable: true,
      openedWidth: `${DRAWER_WIDTH}px`,
      closedWidth: `calc(${theme.spacing(9)} + 1px)`,
    });
    console.log('setRightDrawerOptions');
    return () => {
      console.log('resetRightDrawer');
      resetRightDrawer();
    };
  }, [setRightDrawerOptions, resetRightDrawer, theme]);

  return (
    <Drawer
      open={rightDrawer}
      onClose={() => setRightDrawer(false)}
      variant="permanent"
      anchor="right"
      sx={
        rightDrawer
          ? {
              ...openedMixin(theme),
              '& .MuiDrawer-paper': openedMixin(theme, DRAWER_WIDTH),
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
      <Box display="flex" alignItems="center" sx={{ px: 2, py: 2 }}>
        <Typography
          variant="h6"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          Filter Settings
        </Typography>
        <IconButton onClick={toggleRightDrawer} sx={{ ml: 'auto' }}>
          <FilterSettings />
        </IconButton>
      </Box>
      <Divider />
    </Drawer>
  );
};
