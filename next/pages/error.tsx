import { Box, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NoAuthLayout } from '~/components/layouts/NoAuthLayout';
import { useAuth } from '~/store/userState';

type Props = {
  message?: string;
};

const ErrorPage: NextPage<Props> = ({ message }) => {
  const { user } = useAuth();

  return (
    <Box component={user ? DefaultLayout : NoAuthLayout}>
      <Grid container justifyContent="center" alignItems="flex-end" sx={user && { height: '20vh' }}>
        <Grid item>
          <Typography variant="h4">Error</Typography>
          <Typography>{message || 'An error occurred. Please try again later.'}</Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ErrorPage;
