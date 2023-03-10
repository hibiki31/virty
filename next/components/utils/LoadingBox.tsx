import { Backdrop, CircularProgress, Grid } from '@mui/material';
import { FC } from 'react';

type Props = {
  backdrop?: boolean;
};

export const LoadingBox: FC<Props> = ({ backdrop }) => {
  return backdrop ? (
    <Backdrop sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }} open={true}>
      <CircularProgress />
    </Backdrop>
  ) : (
    <Grid container justifyContent="center" alignItems="center" height="100%">
      <CircularProgress />
    </Grid>
  );
};
