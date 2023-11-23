import { Configuration } from './generated/configuration';
import {
  AuthApi,
  FlavorsApi,
  ImagesApi,
  ImagesTaskApi,
  MixinApi,
  NetworksApi,
  NetworksTaskApi,
  NodesApi,
  NodesTaskApi,
  ProjectsApi,
  StoragesApi,
  StoragesTaskApi,
  TasksApi,
  UsersApi,
  VmsApi,
  VmsTaskApi,
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
export const tasksNodesApi = new NodesTaskApi(config);
export const tasksApi = new TasksApi(config);
export const vmsApi = new VmsApi(config);
export const tasksVmsApi = new VmsTaskApi(config);
export const storagesApi = new StoragesApi(config);
export const imagesApi = new ImagesApi(config);
export const tasksImagesApi = new ImagesTaskApi(config);
export const tasksStoragesApi = new StoragesTaskApi(config);
export const networkApi = new NetworksApi(config);
export const tasksNetworksApi = new NetworksTaskApi(config);
export const projectApi = new ProjectsApi(config);
export const flavorsApi = new FlavorsApi(config);
