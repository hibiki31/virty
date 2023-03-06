import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { FC } from 'react';

export type ConfirmDialogProps = {
  open: boolean;
  title?: string;
  description: string;
  submitText?: string;
  cancelText?: string;
  color?: 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning';
  onClose: () => void;
  onCancel: () => void;
  onSubmit: () => void;
};

export const ConfirmDialog: FC<ConfirmDialogProps> = ({
  open,
  title = 'Confirm',
  description,
  submitText = 'OK',
  cancelText = 'Cancel',
  color = 'primary',
  onClose,
  onCancel,
  onSubmit,
}) => {
  const handleCancelClick = () => {
    onCancel();
    onClose();
  };

  const handleSubmitClick = () => {
    onSubmit();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleCancelClick}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ whiteSpace: 'pre-line' }}>{description}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancelClick} color="inherit">
          {cancelText}
        </Button>
        <Button onClick={handleSubmitClick} variant="contained" disableElevation color={color}>
          {submitText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
