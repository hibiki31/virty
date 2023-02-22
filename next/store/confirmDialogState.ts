import { atom, useRecoilState } from 'recoil';
import { ConfirmDialogProps } from '~/components/dialogs/ConfirmDialog';

export const confirmDialogState = atom<ConfirmDialogProps>({
  key: 'confirmDialog',
  default: {
    open: false,
    title: '',
    description: '',
    onClose: () => {},
    onCancel: () => {},
    onSubmit: () => {},
  },
});

type OpenConfirmDialogProps = Omit<ConfirmDialogProps, 'open' | 'onClose' | 'onCancel' | 'onSubmit'>;

export const useConfirmDialog = () => {
  const [confirmDialogProps, setConfirmDialogProps] = useRecoilState(confirmDialogState);

  const openConfirmDialog = (props: OpenConfirmDialogProps) =>
    new Promise<boolean>((resolve) => {
      setConfirmDialogProps({
        open: true,
        ...props,
        onClose: () => setConfirmDialogProps((beforeProps) => ({ ...beforeProps, open: false })),
        onCancel: () => resolve(false),
        onSubmit: () => resolve(true),
      });
    });

  return { confirmDialogProps, openConfirmDialog };
};
