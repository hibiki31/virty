import { ListItemText, Menu, MenuItem, MenuProps } from '@mui/material';
import { FC } from 'react';

type Props = {
  open?: boolean;
  anchorEl: HTMLElement | null;
  menuProps: Omit<MenuProps, 'open' | 'anchorEl' | 'onClose'>;
  items: {
    primary: string;
    secondary?: string;
    color?: 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning';
    disabled?: boolean;
    onClick: () => void;
  }[];
  onClose: () => void;
};

export const BaseMenu: FC<Props> = ({ open, anchorEl, menuProps, items, onClose }) => {
  const handleMenuClick = (func: () => void) => () => {
    func();
    onClose();
  };

  return (
    <Menu
      {...menuProps}
      open={typeof open === 'undefined' ? !!anchorEl : open}
      anchorEl={anchorEl}
      onClose={onClose}
      sx={{ mt: 1, '& .MuiPaper-root': { minWidth: 200 } }}
    >
      {items.map(({ primary, secondary, color, disabled, onClick }, i) => (
        <MenuItem key={i} onClick={handleMenuClick(onClick)} disabled={disabled}>
          <ListItemText primary={primary} secondary={secondary} primaryTypographyProps={{ color }} />
        </MenuItem>
      ))}
    </Menu>
  );
};
