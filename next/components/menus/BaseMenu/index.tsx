import { ListItemText, Menu, MenuItem, MenuProps } from '@mui/material';
import { ComponentProps, FC, useState } from 'react';

type Item<P> = {
  primary: string;
  secondary?: string;
  color?: 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning';
  disabled?: boolean;
  DialogComponent?: FC<P>;
  dialogProps?: Omit<P, 'open' | 'onClose'>;
  onClick?: () => void;
};

type Props<P> = {
  open?: boolean;
  anchorEl: HTMLElement | null;
  menuProps: Omit<MenuProps, 'open' | 'anchorEl' | 'onClose'>;
  items: Item<P>[];
  onClose: () => void;
};

type BaseMenuComponent = {
  <P = any>(props: Props<P>): JSX.Element;
};

export const BaseMenu: BaseMenuComponent = ({ open, anchorEl, menuProps, items, onClose }) => {
  return (
    <Menu
      {...menuProps}
      open={typeof open === 'undefined' ? !!anchorEl : open}
      anchorEl={anchorEl}
      onClose={onClose}
      sx={{ mt: 1, '& .MuiPaper-root': { minWidth: 200 } }}
    >
      {items.map((item, i) => (
        <CustomMenuItem key={i} item={item} onClose={onClose} />
      ))}
    </Menu>
  );
};

type CustomMenuItemProps<P> = {
  item: Item<P>;
  onClose: () => void;
};

type CustomMenuItemComponent = {
  <P = any>(props: CustomMenuItemProps<P>): JSX.Element;
};

const CustomMenuItem: CustomMenuItemComponent = ({ item, onClose }) => {
  const [open, setOpen] = useState(false);

  const handleMenuClick = (func: () => void) => () => {
    func();
    onClose();
  };

  return !item.DialogComponent ? (
    <MenuItem onClick={handleMenuClick(item.onClick!)} disabled={item.disabled}>
      <ListItemText primary={item.primary} secondary={item.secondary} primaryTypographyProps={{ color: item.color }} />
    </MenuItem>
  ) : (
    <>
      <MenuItem onClick={() => setOpen(true)} disabled={item.disabled}>
        <ListItemText
          primary={item.primary}
          secondary={item.secondary}
          primaryTypographyProps={{ color: item.color }}
        />
      </MenuItem>

      <item.DialogComponent
        {...(item.dialogProps as ComponentProps<typeof item.DialogComponent>)}
        open={open}
        onClose={handleMenuClick(() => setOpen(false))}
      />
    </>
  );
};
