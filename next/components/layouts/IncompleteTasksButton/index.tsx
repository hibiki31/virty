import { Badge, IconButton } from '@mui/material';
import { CheckboxMultipleMarkedOutline } from 'mdi-material-ui';
import { FC } from 'react';
import { NextLink } from '~/components/utils/NextLink';

type Props = {
  count: number;
};

export const IncompleteTasksButton: FC<Props> = ({ count }) => {
  return (
    <NextLink pathname="/tasks" color="inherit">
      <IconButton color="inherit" sx={{ mr: 2, zIndex: 1 }}>
        <Badge badgeContent={count} color="warning">
          <CheckboxMultipleMarkedOutline />
        </Badge>
      </IconButton>
    </NextLink>
  );
};
