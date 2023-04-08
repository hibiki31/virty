import { Box, Container, Toolbar, useMediaQuery, useTheme } from '@mui/material';
import { FC, PropsWithChildren } from 'react';
import { closedMixin, openedMixin } from '~/lib/utils/drawer';
import { useDrawer } from '~/store/drawerState';
import { LoadingBox } from '../utils/LoadingBox';
import { DefaultHeader } from './DefaultHeader';

type Props = PropsWithChildren<{
  isLoading?: boolean;
}>;

export const DefaultLayout: FC<Props> = ({ children, isLoading }) => {
  const { rightDrawer, rightDrawerOptions } = useDrawer();
  const theme = useTheme();
  const isMediumScreen = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box display="flex">
      <DefaultHeader />

      <Container
        component="main"
        maxWidth="xl"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 16px)',
          marginLeft: rightDrawerOptions.enable ? 0 : undefined,
          ...(!isMediumScreen &&
            (rightDrawer
              ? openedMixin(theme, `calc(100% - ${rightDrawerOptions.openedWidth})`)
              : rightDrawerOptions.enable && closedMixin(theme, `calc(100% - ${rightDrawerOptions.closedWidth})`))),
        }}
      >
        <Toolbar />
        {isLoading ? (
          <Box component="div" sx={{ flexGrow: 1 }}>
            <LoadingBox />
          </Box>
        ) : (
          children
        )}
      </Container>
    </Box>
  );
};
