import { Backdrop, CircularProgress, Grid } from '@mui/material';
import { FC } from 'react';

type Props = {
  width?: string | number;
  height?: string | number;
  backdrop?: boolean;
};

export const LoadingBox: FC<Props> = ({ width, height, backdrop }) => {
  return backdrop ? (
    <Backdrop sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }} open={true}>
      <CircularProgress />
    </Backdrop>
  ) : (
    <Grid container justifyContent="center" alignItems="center" width={width} height={height || '100%'}>
      <CircularProgress />
    </Grid>
  );
};
