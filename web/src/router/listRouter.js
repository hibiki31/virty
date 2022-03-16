import VMDetail from '@/views/VMDetail.vue';
import TaskList from '@/views/TaskList.vue';
import NetworkList from '@/views/list/NetworkList.vue';
import NodeList from '@/views/NodeList.vue';
import IssueanceList from '@/views/list/IssueanceList.vue';
import TicketList from '@/views/list/TicketList.vue';
import FlavorList from '@/views/list/FlavorList.vue';
import ProjectList from '@/views/list/ProjectList.vue';

export default {
  routes: [
    {
      path: '/task',
      name: 'TaskList',
      component: TaskList,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/projects',
      name: 'ProjectList',
      component: ProjectList
    },
    {
      path: '/issuances',
      name: 'IssueanceList',
      component: IssueanceList,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/flavors',
      name: 'FlavorList',
      component: FlavorList,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/tickets',
      name: 'TicketList',
      component: TicketList,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/network',
      name: 'NetworkList',
      component: NetworkList,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/node',
      name: 'NodeList',
      component: NodeList,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/vm/:uuid',
      name: 'VMDetail',
      component: VMDetail,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '*',
      redirect: 'VMList'
    }
  ]
};
