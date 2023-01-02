import { FC, PropsWithChildren } from 'react';
import { Container, Typography } from '@mui/material';

export type NoAuthLayoutProps = PropsWithChildren<{}>;

export const NoAuthLayout: FC<NoAuthLayoutProps> = ({ children }) => {
  return (
    <Container sx={{ width: 'fit-content' }}>
      <Typography variant="h2" align="center" mt={15} mb={5}>
        Virty
      </Typography>
      <main>{children}</main>
    </Container>
  );
};
