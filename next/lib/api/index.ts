import { Configuration } from './generated/configuration';
import {
  AuthApi,
  FlavorsApi,
  ImagesApi,
  MixinApi,
  NetworkApi,
  NetworkTaskApi,
  NodesApi,
  ProjectApi,
  StoragesApi,
  TasksApi,
  TasksImagesApi,
  TasksNodesApi,
  TasksStoragesApi,
  UsersApi,
  VmApi,
  VmTaskApi,
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
export const vmsApi = new VmApi(config);
export const tasksVmsApi = new VmTaskApi(config);
export const storagesApi = new StoragesApi(config);
export const imagesApi = new ImagesApi(config);
export const tasksImagesApi = new TasksImagesApi(config);
export const tasksStoragesApi = new TasksStoragesApi(config);
export const networkApi = new NetworkApi(config);
export const tasksNetworksApi = new NetworkTaskApi(config);
export const projectApi = new ProjectApi(config);
export const flavorsApi = new FlavorsApi(config);
