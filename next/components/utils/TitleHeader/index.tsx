import { Box, Divider, Typography } from '@mui/material';
import { FC, PropsWithChildren } from 'react';

type Props = PropsWithChildren<{
  primary: string;
  secondary?: string;
  spacer?: boolean;
}>;

export const TitleHeader: FC<Props> = ({ primary, secondary, spacer, children }) => {
  return (
    <Box display="flex" alignItems="center" sx={{ minHeight: '56px', px: 2, py: 1, gap: 2 }}>
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
