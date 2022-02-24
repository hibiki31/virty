<template>
  <div class="NetworkDetial">
    <network-port-add ref="networkPortAdd" @reload="reload"/>
    <network-port-delete ref="networkPortDelete" @reload="reload" />
    <v-row>
      <v-col cols="12" sm="12" md="12" lg="6">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            <v-icon>mdi-router-network</v-icon>Virtual Port
          </v-card-title>
          <v-card-actions>
            <v-btn @click="$refs.networkPortAdd.openDialog(xmlData,dbData)" small color="primary">
              <v-icon left>mdi-server-plus</v-icon>Add
            </v-btn>
          </v-card-actions>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Name</th>
                  <th class="text-left">VLAN ID</th>
                  <th class="text-left">Default</th>
                  <th class="text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in xmlData.portgroup" :key="`${item.vlanId}`">
                  <td>{{ item.name }}</td>
                  <td>{{ item.vlanId }}</td>
                  <td><v-icon v-if="item.isDefault">mdi-check-bold</v-icon></td>
                  <td>
                    <v-icon
                      small
                      @click="$refs.networkPortDelete.openDialog(item.name, dbData.uuid)"
                    >
                      mdi-delete
                    </v-icon>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from '@/axios/index';
import networkPortAdd from '@/conponents/networks/NetworkPortAdd';
import NetworkPortDelete from '../conponents/networks/NetworkPortDelete.vue';

export default {
  name: 'NetworkDetial',
  components: {
    networkPortAdd,
    NetworkPortDelete
  },
  data: () => ({
    dbData: {},
    xmlData: {}
  }),
  async mounted() {
    this.reload();
  },
  methods: {
    async reload() {
      await axios.get(`/api/networks/${this.$route.params.uuid}`)
        .then((res) => {
          this.dbData = res.data.db;
          this.xmlData = res.data.xml;
        });
    }
  }
};
</script>
