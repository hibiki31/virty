export const TASK_STATUS = {
  FINISH: 'finish',
  INIT: 'init',
  ERROR: 'error',
} as const;

export const TASK_METHOD = {
  POST: 'post',
  PUT: 'put',
  DELETE: 'delete',
} as const;

export const TASK_RESOURCE = {
  VM: 'vm',
  NODE: 'node',
  STORAGE: 'storage',
  NETWORK: 'network',
} as const;
