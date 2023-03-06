import { Breakpoint, Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { FC, PropsWithChildren, ReactNode } from 'react';

export type Props = PropsWithChildren<{
  title: ReactNode;
  submitText?: string;
  open: boolean;
  deletable?: boolean;
  submitDisabled?: boolean;
  maxWidth?: Breakpoint;
  persistent?: boolean;
  onClose: () => void;
  onSubmit?: () => void;
  onDelete?: () => void;
}>;

export const BaseDialog: FC<Props> = ({
  title,
  submitText = 'Submit',
  open,
  deletable = false,
  submitDisabled,
  maxWidth = 'xs',
  persistent = false,
  onClose,
  onSubmit,
  onDelete,
  children,
}) => {
  return (
    <Dialog maxWidth={maxWidth} fullWidth open={open} onClose={!persistent ? onClose : undefined}>
      <DialogTitle>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>{title}</Grid>
          {deletable && (
            <Grid item>
              <IconButton color="error" size="small" onClick={onDelete}>
                <DeleteIcon />
              </IconButton>
            </Grid>
          )}
        </Grid>
      </DialogTitle>
      <DialogContent sx={{ pt: '10px !important' }}>{children}</DialogContent>
      {onSubmit && (
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={onSubmit} variant="contained" disableElevation disabled={submitDisabled}>
            {submitText}
          </Button>
        </DialogActions>
      )}
    </Dialog>
  );
};
