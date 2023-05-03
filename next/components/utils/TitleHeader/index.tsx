import { Box, Divider, Typography } from '@mui/material';
import { FC, PropsWithChildren, ReactNode } from 'react';

type Props = PropsWithChildren<{
  primary: ReactNode;
  secondary?: ReactNode;
  prefix?: ReactNode;
  spacer?: boolean;
}>;

export const TitleHeader: FC<Props> = ({ primary, secondary, prefix, spacer, children }) => {
  return (
    <Box display="flex" alignItems="center" sx={{ minHeight: '56px', px: 2, py: 1, gap: 2 }}>
      {prefix}
      <Typography variant="h5">{primary}</Typography>
      {secondary && (
        <>
          <Divider orientation="vertical" flexItem />
          <Typography variant="subtitle1">{secondary}</Typography>
        </>
      )}
      {spacer && <Box sx={{ flexGrow: 1 }} />}
      {children}
    </Box>
  );
};
