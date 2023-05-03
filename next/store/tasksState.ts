import { atom, useRecoilState, useRecoilValue } from 'recoil';
import useSWR from 'swr';
import { tasksApi } from '~/lib/api';
import { IncompleteTasksResponse } from '~/lib/api/task';
import { useAuth } from './userState';

type incompleteTasksState = {
  count: number;
  updateHash: string;
};

export const incompleteTasksState = atom<incompleteTasksState>({
  key: 'incompleteTasks',
  default: {
    count: 0,
    updateHash: '',
  },
});

export const useGetIncompleteTasks = () => {
  const [incompleteTasks, setIncompleteTasks] = useRecoilState(incompleteTasksState);
  const { user } = useAuth();

  // long polling
  useSWR(
    ['tasksApi.getTasksIncompleteApiTasksIncompleteGet', incompleteTasks?.updateHash, user?.isAdminMode],
    ([, updateHash, isAdminMode]) =>
      isAdminMode !== undefined
        ? tasksApi.getTasksIncompleteApiTasksIncompleteGet(updateHash, isAdminMode).then((res) => {
            const data: IncompleteTasksResponse = res.data;
            setIncompleteTasks({
              count: data.task_count,
              updateHash: data.task_hash,
            });
          })
        : undefined,
    {
      revalidateOnFocus: false,
      refreshInterval: 1, // For refresh even if updateHash is not changed
    }
  );

  return incompleteTasks;
};

export const useIncompleteTasks = () => {
  return useRecoilValue(incompleteTasksState);
};
