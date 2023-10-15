import { atom, useRecoilState, useRecoilValue } from 'recoil';
import useSWR from 'swr';
import { tasksApi } from '~/lib/api';
import { useAuth } from './userState';

type incompleteTasksState = {
  count: number;
  hash: string;
};

export const incompleteTasksState = atom<incompleteTasksState>({
  key: 'incompleteTasks',
  default: {
    count: 0,
    hash: '',
  },
});

export const useGetIncompleteTasks = () => {
  const [incompleteTasks, setIncompleteTasks] = useRecoilState(incompleteTasksState);
  const { user } = useAuth();

  // long polling
  useSWR(
    ['tasksApi.getIncompleteTasks', incompleteTasks.hash, user?.isAdminMode],
    ([, hash, isAdminMode]) =>
      isAdminMode !== undefined
        ? tasksApi.getIncompleteTasks(hash, isAdminMode).then((res) => setIncompleteTasks(res.data))
        : undefined,
    {
      revalidateOnFocus: false,
      refreshInterval: 1, // For refresh even if hash is not changed
    }
  );

  return incompleteTasks;
};

export const useIncompleteTasks = () => {
  return useRecoilValue(incompleteTasksState);
};
