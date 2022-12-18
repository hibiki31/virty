import { Configuration } from './generated/configuration';
import {
  AuthApi,
  FlavorsApi,
  MetricsApi,
  NetworkApi,
  NodeApi,
  ProjectApi,
  StorageApi,
  TasksApi,
  TicketsApi,
  UserApi,
  VmsApi,
} from './generated/api';

const { NEXT_PUBLIC_API_URL } = process.env;

const config = new Configuration({
  basePath: NEXT_PUBLIC_API_URL,
});

export const authApi = new AuthApi(config);
export const flavorsApi = new FlavorsApi(config);
export const metricsApi = new MetricsApi(config);
export const networkApi = new NetworkApi(config);
export const nodeApi = new NodeApi(config);
export const projectApi = new ProjectApi(config);
export const storageApi = new StorageApi(config);
export const tasksApi = new TasksApi(config);
export const ticketsApi = new TicketsApi(config);
export const userApi = new UserApi(config);
export const vmsApi = new VmsApi(config);
