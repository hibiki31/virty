import { Box, Card, Link, Typography } from '@mui/material';
import { Console, OpenInNew } from 'mdi-material-ui';
import { FC, memo, useEffect, useState } from 'react';
import { LoadingBox } from '~/components/utils/LoadingBox';
import { VM_STATUS } from '~/lib/api/vm';

const { NEXT_PUBLIC_NOVNC_FQDN } = process.env;

interface ExtendedNoVncClient {
  toBlob: (callback: BlobCallback, type?: string, quality?: any) => void;
}

type Props = {
  uuid: string;
  status: number;
};

export const VMConsoleCard: FC<Props> = memo(function NotMemoVMConsoleCard({ uuid, status }) {
  const [imageUrl, setImageUrl] = useState<string | undefined>(undefined);
  const [disconnected, setDisconnected] = useState<boolean>(false);

  useEffect(() => {
    if (status !== VM_STATUS.POWER_ON) {
      return;
    }
    import('@novnc/novnc/core/rfb').then(({ default: RFB }) => {
      const el = document.createElement('div');
      const rfb = new RFB(
        el,
        `wss://${NEXT_PUBLIC_NOVNC_FQDN || window.location.host}/novnc/websockify?token=${uuid}`
      ) as InstanceType<typeof RFB> & ExtendedNoVncClient;
      rfb.addEventListener('connect', async () => {
        const blob: Blob | null = await new Promise((resolve) => {
          setTimeout(() => {
            rfb.toBlob(resolve);
          }, 500);
        });
        if (blob) {
          setImageUrl(URL.createObjectURL(blob));
        }
        rfb.disconnect();
      });
      rfb.addEventListener('disconnect', () => {
        setDisconnected(true);
      });
    });
  }, [uuid, status]);

  const consoleUrl = `https://${
    NEXT_PUBLIC_NOVNC_FQDN || window.location.host
  }/novnc/vnc.html?resize=remote&autoconnect=true&path=novnc/websockify?token=${uuid}`;

  return (
    <Card sx={{ width: '100%', height: '100%', backgroundColor: 'grey.700' }}>
      <Box display="flex" justifyContent="center" alignItems="center" maxWidth={384} minHeight={288} margin="auto">
        {status !== VM_STATUS.POWER_ON ? (
          <Typography variant="h6">VM is not running</Typography>
        ) : imageUrl ? (
          <Link
            href={consoleUrl}
            target="_blank"
            underline="none"
            color="inherit"
            position="relative"
            display="flex"
            justifyContent="center"
            alignItems="center"
          >
            <Box
              component="img"
              src={imageUrl}
              alt="VM Console"
              sx={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
            <Box position="absolute">
              <Console />
              <OpenInNew />
            </Box>
          </Link>
        ) : disconnected ? (
          <Typography variant="h6">Failed to connect to console</Typography>
        ) : (
          <LoadingBox width="100%" height="100%" />
        )}
      </Box>
    </Card>
  );
});
