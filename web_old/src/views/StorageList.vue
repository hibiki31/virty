<template>
  <div>
    <StorageAddDialog ref="storageAddDialog" @reload="reload"/>
    <StorageDeleteDialog ref="storageDeleteDialog"  @reload="reload"/>
    <storage-pool-add-dialog ref="storagePoolAddDialog"  @reload="reload"/>
    <storage-metadata-edit ref="storageMetadataEditdialog" @reload="reload" />
    <storage-pool-join-dialog ref="storagePoolJoinDialog" @reload="reload" />
    <v-card>
      <v-card-actions>
        <v-btn v-on:click="this.storageReloadTask" small dark class="ma-2" color="primary">
          <v-icon left>mdi-cached</v-icon>Reload list
        </v-btn>
        <v-btn v-on:click="this.openAddDialog" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>register Storage
        </v-btn>
      </v-card-actions>
      <v-data-table
        :headers="headers"
        :items="list"
        :items-per-page="10"
        :loading="loading"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100],
          showFirstLastPage: true,
            }"
        multi-sort
      >
        <template v-slot:[`item.capacity`]="{ item }" justify="right">
          {{item.capacity}} GB
        </template>
        <template v-slot:[`item.used`]="{ item }" justify="right">
          {{item.capacity-item.available}} GB
        </template>
        <template v-slot:[`item.available`]="{ item }" justify="right">
          <v-progress-linear
            color="primary"
            height="20"
            :value="(item.capacity-item.available)/item.capacity*100"
          >
            <strong>{{item.available}} GB</strong>
          </v-progress-linear>
        </template>
        <template v-slot:[`item.overcommit`]="{ item }">
          <strong v-if='(item.capacityCommit - item.allocationCommit - item.available) > 0' class="error--text">
            {{ item.capacityCommit - item.allocationCommit - item.available}} GB
          </strong>
          <strong v-else class="primary--text">
            {{ item.capacityCommit - item.allocationCommit - item.available}} GB
          </strong>
        </template>

        <template v-slot:[`item.actions`]="{ item }">
          <v-icon small @click="openDeleteDialog(item)">mdi-delete</v-icon>
          <v-icon small @click="openMetadataEditDialog(item)">mdi-pen</v-icon>
          <v-icon v-on:click="$refs.storagePoolJoinDialog.openDialog(item)" small left>mdi-server-plus</v-icon>
        </template>
      </v-data-table>
    </v-card>
    <v-card class="mt-5">
      <v-card-actions>
         <v-btn v-on:click="$refs.storagePoolAddDialog.openDialog()" small class="ma-2" color="primary">
          <v-icon left>mdi-server-plus</v-icon>Create Storage Pool
        </v-btn>
      </v-card-actions>
      <v-data-table
        :headers="headersPools"
        :items="listPools"
        :items-per-page="10"
        :loading="loading"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100],
          showFirstLastPage: true,
            }"
        multi-sort
      >
      <template v-slot:[`item.storages`]="{ item }">
            <v-chip
              v-for="storage in item.storages"
              :key="storage.storage.uuid"
              class="ma-2"
              label
              small
            >
              {{ storage.storage.name }}@{{ storage.storage.nodeName }}
            </v-chip>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';
import StorageAddDialog from '../conponents/storages/StorageAddDialog';
import StoragePoolAddDialog from '@/conponents/storages/StoragePoolAddDialog';
import StorageDeleteDialog from '../conponents/storages/StorageDeleteDialog';
import StorageMetadataEdit from '../conponents/storages/StorageMetadataEdit.vue';
import StoragePoolJoinDialog from '../conponents/storages/StoragePoolJoinDialog.vue';

export default {
  name: 'StorageList',
  components: {
    StoragePoolAddDialog,
    StorageAddDialog,
    StorageDeleteDialog,
    StorageMetadataEdit,
    StoragePoolJoinDialog
  },
  data: function() {
    return {
      list: [],
      listPools: [],
      loading: false,
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Node', value: 'nodeName' },
        { text: 'UUID', value: 'uuid' },
        { text: 'Capacity', value: 'capacity' },
        { text: 'Used', value: 'used' },
        { text: 'Available', value: 'available' },
        { text: 'OverCommit', value: 'overcommit', align: 'right' },
        { text: 'active', value: 'active' },
        { text: 'auto', value: 'autoStart' },
        { text: 'Path', value: 'path' },
        { text: 'Device', value: 'metaData.deviceType' },
        { text: 'Protocol', value: 'metaData.protocol' },
        { text: 'Rool', value: 'metaData.rool' },
        { text: 'Actions', value: 'actions' }
      ],
      headersPools: [
        { text: 'id', value: 'id' },
        { text: 'name', value: 'name' },
        { text: 'storages', value: 'storages' }
      ]
    };
  },
  mounted: function() {
    this.reload();
  },
  methods: {
    async reload() {
      this.loading = true;
      await axios.get('/api/storages').then((response) => (this.list = response.data));
      await axios.get('/api/storages/pools').then((response) => (this.listPools = response.data));
      this.loading = false;
    },
    openDeleteDialog(item) {
      this.$refs.storageDeleteDialog.openDialog(item);
    },
    openMetadataEditDialog(item) {
      this.$refs.storageMetadataEditdialog.openDialog(item);
    },
    openAddDialog() {
      this.$refs.storageAddDialog.openDialog();
    },
    storageReloadTask() {
      axios
        .put('/api/images')
        .then((res) => {
          if (res.status === 401) {
            this.$_pushNotice('Wrong userID or password', 'error');
          } else if (res.status !== 200) {
            this.$_pushNotice('An error occurred', 'error');
            return;
          }
          this.$_pushNotice('Queueing Relaod task', 'success');
        })
        .catch(async() => {
          await this.$_sleep(500);
          this.$_pushNotice('An error occurred', 'error');
        });
    },
    getPowerColor(statusCode) {
      if (statusCode === 'success') return 'blue';
      else if (statusCode === 'init') return 'grey lighten-1';
      else if (statusCode === 'error') return 'red';
      else return 'yellow';
    }
  }
};
</script>
