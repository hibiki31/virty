import { Button, ButtonProps, IconButton, IconButtonProps } from '@mui/material';
import { ComponentProps, FC, MouseEvent, ReactNode, useState } from 'react';

type Props<P> = {
  label?: ReactNode;
  useIconButton?: boolean;
  MenuComponent: FC<P>;
  buttonProps?: Props<P>['useIconButton'] extends true ? IconButtonProps : ButtonProps;
  menuProps?: Omit<P, 'open' | 'anchorEl' | 'onClose'>;
};

type OpenMenuButtonComponent = {
  <P = any>(props: Props<P>): JSX.Element;
};

export const OpenMenuButton: OpenMenuButtonComponent = ({
  label,
  useIconButton,
  MenuComponent,
  buttonProps,
  menuProps,
}) => {
  const [open, setOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuClick = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    setOpen(true);
  };

  return (
    <>
      {useIconButton ? (
        <IconButton {...buttonProps} onClick={handleMenuClick}>
          {label}
        </IconButton>
      ) : (
        <Button {...buttonProps} onClick={handleMenuClick}>
          {label}
        </Button>
      )}

      <MenuComponent
        {...(menuProps as ComponentProps<typeof MenuComponent>)}
        open={open}
        anchorEl={anchorEl}
        onClose={() => setOpen(false)}
      />
    </>
  );
};
