import { Box, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NoAuthLayout } from '~/components/layouts/NoAuthLayout';
import { useAuth } from '~/store/userState';

const Error404Page: NextPage = () => {
  const { user } = useAuth();

  return (
    <Box component={user ? DefaultLayout : NoAuthLayout}>
      <Grid container justifyContent="center" alignItems="flex-end" sx={user && { height: '20vh' }}>
        <Grid item>
          <Typography variant="h4">404</Typography>
          <Typography>This page could not be found.</Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Error404Page;
