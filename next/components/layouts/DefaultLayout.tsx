import { Box, Container, Toolbar } from '@mui/material';
import { FC, PropsWithChildren } from 'react';
import { DefaultHeader } from './DefaultHeader';
import { NavigationDrawer } from './NavigationDrawer';

export const DefaultLayout: FC<PropsWithChildren> = ({ children }) => {
  return (
    <Box component="div" sx={{ display: 'flex' }}>
      <DefaultHeader />
      <NavigationDrawer />
      <Container component="main" sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 16px)' }}>
        <Toolbar />
        {children}
      </Container>
    </Box>
  );
};
