import { Link, TypographyProps } from '@mui/material';
import Nextlink from 'next/link';
import { FC, PropsWithChildren } from 'react';

type Props = PropsWithChildren<{
  pathname: string;
  underline?: 'none' | 'hover' | 'always';
  color?: TypographyProps['color'];
}>;

export const NextLink: FC<Props> = ({ pathname, underline, color, children }) => {
  return (
    <Nextlink href={{ pathname }} passHref>
      <Link underline={underline} color={color}>
        {children}
      </Link>
    </Nextlink>
  );
};
