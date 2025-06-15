<template>
  <v-card>
    <v-data-table :headers="headers" :items="list.data" :items-per-page="10">
      <template v-slot:item.status="{ value }">
        <v-chip :border="`${getStatusColor(value)} thin opacity-25`" :color="getStatusColor(value)" :text="value"
          size="small"></v-chip>
      </template>
      <template v-slot:item.postTime="{ value }">
        {{ toJST(value) }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts" setup>
import { reactive } from 'vue'
import { apiClient } from '@/api'

import type { paths } from '@/api/openapi'

import { format, parse, parseISO } from 'date-fns'
import ja from 'date-fns/locale/ja'

const list = ref<paths['/api/tasks']['get']['responses']['200']['content']['application/json']>({
  count: 0,
  data: [],
})

apiClient.GET('/api/tasks', {
  params: {
    query: {
      admin: true,
      limit: 100,
    }
  }
}).then((res) => {
  if (res.data) {
    list.value = res.data
  }
})

let headers = [
  { text: 'Status', value: 'status' },
  { text: 'PostTime', value: 'postTime' },
  { text: 'Request', value: 'resource' },
  { text: 'Method', value: 'method' },
  { text: 'userId', value: 'userId' },
  { text: 'ID', value: 'uuid' },
  { text: 'TunTime', value: 'runTime' }
]

// const methodTransration = (method) => {
//   switch (method) {
//     case 'add': return 'POST';
//     case 'update': return 'PUT';
//     case 'delete': return 'DELETE';
//     case 'cahnge': return 'PATH';
//   }
// }

// const copyClipBoard = (text) => {
//   this.$copyText(text).then(function (e) {
//     console.log(e);
//   }, function (e) {
//     console.log(e);
//   });
// }

// const copyClipBoardCurl = (item) => {
//   const comand = `curl -X '${this.methodTransration(item.method)}' \\
// '${location.protocol}//${location.host}/api/${item.resource}/${item.object}' \\
// -H 'accept: application/json' \\
// -H 'Authorization: Bearer ${this.$store.state.userData.token}' \\
// -d '${JSON.stringify(item.request)}'`;
//   this.$copyText(comand).then(function (e) {
//     console.log(e);
//   }, function (e) {
//     console.log(e);
//   });
// }



// const openTaskDeleteDialog = () => {
//   this.$refs.taskDeleteDialog.openDialog();
// }


const getStatusColor = (statusCode) => {
  if (statusCode === 'finish') return 'primary';
  else if (statusCode === 'init') return 'grey lighten-1';
  else if (statusCode === 'error') return 'error';
  else return 'yellow';
}

// const getMethodColor = (statusCode) => {
//   if (statusCode === 'post') return 'success';
//   else if (statusCode === 'put') return 'primary';
//   else if (statusCode === 'delete') return 'error';
//   else return 'yellow';
// }
// const getResourceIcon = (resource) => {
//   if (resource === 'vm') return 'mdi-cube-outline';
//   else if (resource === 'node') return 'mdi-server';
//   else if (resource === 'storage') return 'mdi-database';
//   else if (resource === 'network') return 'mdi-wan';
//   else return 'mdi-help-rhombus';
// }

const toJST = (val) => {
  return format(parseISO(val), 'yyyy-MM-dd HH:mm', { locale: ja })
}

const toFixedTow = (val) => {
  if (isFinite(val)) {
    return Number(val).toFixed(2);
  }
  return 0;
}



</script>
