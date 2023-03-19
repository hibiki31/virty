import { Configuration } from './generated/configuration';
import {
  AuthApi,
  FlavorsApi,
  ImagesApi,
  MixinApi,
  NetworkApi,
  NodesApi,
  ProjectApi,
  StoragesApi,
  TasksApi,
  TasksImagesApi,
  TasksNodesApi,
  TasksStoragesApi,
  UsersApi,
  VmsApi,
} from './generated/api';
import { parseCookies } from 'nookies';

const { NEXT_PUBLIC_API_URL } = process.env;

const config = new Configuration({
  basePath: NEXT_PUBLIC_API_URL,
  accessToken: () => {
    const { token } = parseCookies();
    return token;
  },
});

export const mixinApi = new MixinApi(config);
export const authApi = new AuthApi(config);
export const usersApi = new UsersApi(config);
export const nodesApi = new NodesApi(config);
export const tasksNodesApi = new TasksNodesApi(config);
export const tasksApi = new TasksApi(config);
export const vmsApi = new VmsApi(config);
export const storagesApi = new StoragesApi(config);
export const imagesApi = new ImagesApi(config);
export const tasksImagesApi = new TasksImagesApi(config);
export const tasksStoragesApi = new TasksStoragesApi(config);
export const networkApi = new NetworkApi(config);
export const projectApi = new ProjectApi(config);
export const flavorsApi = new FlavorsApi(config);
