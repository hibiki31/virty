import { Box, Container, Toolbar } from '@mui/material';
import { FC, PropsWithChildren } from 'react';
import { LoadingBox } from '../utils/LoadingBox';
import { DefaultHeader } from './DefaultHeader';

type Props = PropsWithChildren<{
  isLoading?: boolean;
}>;

export const DefaultLayout: FC<Props> = ({ children, isLoading }) => {
  return (
    <Box display="flex">
      <DefaultHeader />

      <Container
        component="main"
        maxWidth="xl"
        sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 16px)' }}
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
