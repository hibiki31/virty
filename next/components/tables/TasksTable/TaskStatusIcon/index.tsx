import { Alert, CheckCircle, HelpRhombus, PlayCircle, RefreshCircle, TextBoxRemove, TimerSand } from 'mdi-material-ui';
import { FC } from 'react';
import { TASK_STATUS } from '~/lib/api/task';

type Props = {
  status: string;
};

export const TaskStatusIcon: FC<Props> = ({ status }) => {
  const color =
    status === TASK_STATUS.FINISH
      ? 'primary.main'
      : status === TASK_STATUS.INIT
      ? 'grey.500'
      : status === TASK_STATUS.ERROR
      ? 'error.main'
      : 'warning.main';
  switch (status) {
    case TASK_STATUS.START:
      return <PlayCircle sx={{ color }} />;
    case TASK_STATUS.FINISH:
      return <CheckCircle sx={{ color }} />;
    case TASK_STATUS.INIT:
      return <RefreshCircle sx={{ color }} />;
    case TASK_STATUS.WAIT:
      return <TimerSand sx={{ color }} />;
    case TASK_STATUS.ERROR:
      return <Alert sx={{ color }} />;
    case TASK_STATUS.LOST:
      return <TextBoxRemove sx={{ color }} />;
  }
  return <HelpRhombus sx={{ color }} />;
};
