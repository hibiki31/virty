import { FC, ReactNode } from 'react';
import {
  IconButton,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableCellProps,
  Link,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import NextLink from 'next/link';

type Props<P = Record<string, any>> = {
  isLoading?: boolean;
  cols: {
    name?: ReactNode;
    align?: TableCellProps['align'];
    width?: string | number;
    getItem: (item: P, i: number) => ReactNode;
    getUrl?: (item: P, i: number) => string;
  }[];
  items: P[];
  onClick?: (item: P) => void;
  hiddenHeader?: boolean;
  hiddenBorder?: boolean;
  disableElevation?: boolean;
  dense?: boolean;
};

type BaseTableComponent = {
  <P = any>(props: Props<P>): JSX.Element;
};

export const BaseTable: BaseTableComponent = ({
  isLoading = false,
  cols,
  items,
  onClick,
  hiddenHeader,
  hiddenBorder,
  disableElevation,
  dense,
}) => {
  return (
    <TableContainer component={disableElevation ? 'div' : Paper}>
      {isLoading && <LinearProgress />}
      <Table size={dense ? 'small' : 'medium'}>
        {!hiddenHeader && (
          <TableHead>
            <TableRow sx={hiddenBorder ? { '& td, & th': { border: 'none' } } : undefined}>
              {cols.map((col, i) => (
                <TableCell key={i} align={col.align} sx={{ width: col.width }}>
                  {col.name}
                </TableCell>
              ))}
              {onClick && <TableCell />}
            </TableRow>
          </TableHead>
        )}
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={cols.length + Number(!!onClick)}>Loading...</TableCell>
            </TableRow>
          ) : (
            !items.length && (
              <TableRow>
                <TableCell colSpan={cols.length + Number(!!onClick)}>No items found.</TableCell>
              </TableRow>
            )
          )}
          {items.map((item, i) => (
            <TableRow
              key={i}
              sx={{
                '&:last-child td, &:last-child th': { border: 'none' },
                ...(hiddenBorder ? { '& td, & th': { border: 'none' } } : {}),
              }}
            >
              {cols.map((col, j) => (
                <TableCell key={j} align={col.align}>
                  {col.getUrl ? (
                    <NextLink href={col.getUrl(item, i)} passHref>
                      <Link>{col.getItem(item, i)}</Link>
                    </NextLink>
                  ) : (
                    col.getItem(item, i)
                  )}
                </TableCell>
              ))}
              {onClick && (
                <TableCell align="center">
                  <IconButton size="small" onClick={() => onClick(item)}>
                    <MoreVertIcon />
                  </IconButton>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
