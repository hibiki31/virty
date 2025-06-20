<template>
  <div>
    <project-add-dialog ref="addDialog" @reload="reload"/>
    <project-put-dialog ref="putDialog" @reload="reload"/>
    <project-delete-dialog ref="deleteDialog" @reload="reload"/>
    <v-card>
      <v-card-actions>
        <v-btn
          v-on:click="$refs.addDialog.openDialog()"
          small
          dark
          class="ma-2"
          color="primary"
        >
          <v-icon left>mdi-folder-star</v-icon>CREATE
        </v-btn>
      </v-card-actions>
      <v-data-table
        :loading="tableLoading"
        :headers="headers"
        :items="ListProjects"
        :items-per-page="20"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100, 200, 300, 400, 500],
          showFirstLastPage: true,
        }"
        multi-sort
      >
        <template v-slot:[`item.users`]="{ item }" justify="right">
          <v-chip
            v-for="user in item.users"
            :key="user.id"
            class="ma-2"
            close
            small
          >
            {{ user.id }}
          </v-chip>
        </template>
        <template v-slot:[`item.actions`]="{ item }" justify="right">
          <v-btn
            v-on:click="$refs.putDialog.openDialog(item)"
            small
            icon
          >
            <v-icon class="ma-2 mr-5" left>mdi-account-multiple-plus</v-icon>
          </v-btn>
          <v-btn
            v-on:click="$refs.deleteDialog.openDialog(item)"
            small
            icon
          >
            <v-icon class="ma-2" left>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import ProjectAddDialog from '@/conponents/projects/ProjectAddDialog.vue';
import ProjectPutDialog from '@/conponents/projects/ProjectPutDialog.vue';
import ProjectDeleteDialog from '@/conponents/projects/ProjectDeleteDialog.vue';

export default {
  name: 'ProjectList',
  components: {
    ProjectAddDialog,
    ProjectPutDialog,
    ProjectDeleteDialog
  },
  data: function() {
    return {
      tableLoading: true,
      headers: [
        { text: 'name', value: 'name' },
        { text: 'id', value: 'id' },
        { text: 'cpu limit', value: 'core' },
        { text: 'memory limit', value: 'memoryG' },
        { text: 'cpu used', value: 'usedCore' },
        { text: 'memory used', value: 'usedMemoryG' },
        { text: 'sotrage capacity', value: 'storageCapacityG' },
        { text: 'users', value: 'users' },
        { text: 'actions', value: 'actions' }
      ],
      user: [],
      ListProjects: []
    };
  },
  mounted: async function() {
    this.reload();
  },
  methods: {
    async reload() {
      this.tableLoading = true;
      await axios.get('/api/users').then((response) => (this.user = response.data));
      await axios.get('/api/projects', {
        params: {
          admin: this.$store.state.userData.adminMode
        }
      }).then((response) => (this.ListProjects = response.data));

      this.tableLoading = false;
    }
  }
};
</script>
