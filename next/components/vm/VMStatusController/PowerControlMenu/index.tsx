import { FC } from 'react';
import { BaseMenu } from '~/components/menus/BaseMenu';

type Props = {
  open: boolean;
  anchorEl: HTMLElement | null;
  onClose: () => void;
};

export const PowerControlMenu: FC<Props> = ({ open, anchorEl, onClose }) => {
  return (
    <BaseMenu
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      items={[
        {
          primary: 'Power ON',
          onClick: () => console.log('Power ON'),
        },
        {
          primary: 'Power OFF',
          color: 'error',
          onClick: () => console.log('Power OFF'),
        },
      ]}
    />
  );
};
