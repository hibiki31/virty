import { Breakpoint, Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@mui/material';
import { FC, PropsWithChildren, ReactNode } from 'react';
import { LoadingButton } from '@mui/lab';

type Props = PropsWithChildren<{
  title: ReactNode;
  submitText?: string;
  open: boolean;
  headerActions?: ReactNode;
  submitDisabled?: boolean;
  submitLoading?: boolean;
  maxWidth?: Breakpoint;
  persistent?: boolean;
  disabledPadding?: boolean;
  onClose: () => void;
  onSubmit?: () => void;
}>;

export const BaseDialog: FC<Props> = ({
  title,
  submitText = 'Submit',
  open,
  headerActions,
  submitDisabled,
  submitLoading,
  maxWidth = 'xs',
  persistent = false,
  disabledPadding = false,
  onClose,
  onSubmit,
  children,
}) => {
  return (
    <Dialog maxWidth={maxWidth} fullWidth open={open} onClose={!persistent ? onClose : undefined}>
      <DialogTitle>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>{title}</Grid>
          {headerActions && <Grid item>{headerActions}</Grid>}
        </Grid>
      </DialogTitle>
      <DialogContent sx={{ pt: '10px !important', p: disabledPadding ? 0 : undefined }}>{children}</DialogContent>
      {onSubmit && (
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <LoadingButton
            onClick={onSubmit}
            variant="contained"
            disableElevation
            disabled={submitDisabled}
            loading={submitLoading}
          >
            {submitText}
          </LoadingButton>
        </DialogActions>
      )}
    </Dialog>
  );
};
