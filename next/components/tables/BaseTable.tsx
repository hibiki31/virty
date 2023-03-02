import { FC } from 'react';
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

type Props = {
  isLoading?: boolean;
  cols: {
    name?: string;
    align?: TableCellProps['align'];
    getItem: (item: Record<string, any>) => string | number | undefined;
    getUrl?: (item: Record<string, any>) => string;
  }[];
  items: Record<string, any>[];
  onClick?: (item: Record<string, any>) => void;
  hiddenHeader?: boolean;
  hiddenBorder?: boolean;
  disableElevation?: boolean;
  dense?: boolean;
};

export const BaseTable: FC<Props> = ({
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
            <TableRow>
              {cols.map((col, i) => (
                <TableCell key={i} align={col.align}>
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
              {cols.map((col, i) => (
                <TableCell key={i} align={col.align}>
                  {col.getUrl ? (
                    <NextLink href={col.getUrl(item)} passHref>
                      <Link>{col.getItem(item)}</Link>
                    </NextLink>
                  ) : (
                    col.getItem(item)
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
