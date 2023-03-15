import { Button, ButtonProps, IconButton, IconButtonProps } from '@mui/material';
import { ComponentProps, FC, ReactNode, useState } from 'react';

type Props<P> = {
  label?: ReactNode;
  useIconButton?: boolean;
  DialogComponent: FC<P>;
  buttonProps?: Props<P>['useIconButton'] extends true ? IconButtonProps : ButtonProps;
  dialogProps?: Omit<P, 'open' | 'onClose'>;
};

type OpenDialogButtonComponent = {
  <P = any>(props: Props<P>): JSX.Element;
};

export const OpenDialogButton: OpenDialogButtonComponent = ({
  label,
  useIconButton,
  DialogComponent,
  buttonProps,
  dialogProps,
}) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      {useIconButton ? (
        <IconButton {...buttonProps} onClick={() => setOpen(true)}>
          {label}
        </IconButton>
      ) : (
        <Button {...buttonProps} onClick={() => setOpen(true)}>
          {label}
        </Button>
      )}

      <DialogComponent
        {...(dialogProps as ComponentProps<typeof DialogComponent>)}
        open={open}
        onClose={() => setOpen(false)}
      />
    </>
  );
};
