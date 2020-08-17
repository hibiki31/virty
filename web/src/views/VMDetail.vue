<template>
  <div class="VMDetail">
    <p class="title"><v-icon>mdi-desktop-classic</v-icon>{{ data.name }}</p>
    <v-row>
          <v-col cols="12" sm="6" md="4" lg="3">
            <v-card>
            <v-card-title class="subheading font-weight-bold">
              <v-icon>mdi-transit-connection-variant</v-icon>VNC
            </v-card-title>
            <v-list class="body-2" dense>
              <v-list-item>
                <v-list-item-content>Name</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.name }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Node</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.node_name }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Memory</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.memory / 1024 }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>CPU</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.vcpu }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>UUID</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.uuid }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>SELinux</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.selinux }}</v-list-item-content>
              </v-list-item>
            </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" lg="3">
            <v-card>
            <v-card-title class="subheading font-weight-bold">
              <v-icon>mdi-transit-connection-variant</v-icon>VNC
            </v-card-title>
            <v-list class="body-2" dense>
              <v-list-item>
                <v-list-item-content>Host</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.node_ }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Node</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.node_name }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>VNC Port</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.vncPort }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Protein:</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.protein }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Sodium:</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.sodium }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Calcium:</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.calcium }}</v-list-item-content>
              </v-list-item>

              <v-list-item>
                <v-list-item-content>Iron:</v-list-item-content>
                <v-list-item-content class="align-end">{{ data.iron }}</v-list-item-content>
              </v-list-item>
            </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="4" lg="6">
            <v-card>
            <v-card-title class="subheading font-weight-bold">
              <v-icon>mdi-router-network</v-icon>Network
            </v-card-title>
            <v-simple-table>
              <template v-slot:default>
                <thead>
                  <tr>
                    <th class="text-left">Type</th>
                    <th class="text-left">MAC address</th>
                    <th class="text-left">Terget</th>
                    <th class="text-left">Source</th>
                    <th class="text-left">Network Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in data.interface" :key="item.macAddress">
                    <td>{{ item.type }}</td>
                    <td>{{ item.macAddress }}</td>
                    <td>{{ item.terget }}</td>
                    <td>{{ item.source }}</td>
                    <td>{{ item.network }}</td>
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
// @ is an alias to /src
import axios from '@/axios/index';

export default {
  name: 'VMDetail',
  data: () => ({
    data: {}
  }),
  async mounted() {
    await axios
      .get(`/api/vm/${this.$route.params.uuid}`)
      .then(res => {
        this.data = res.data;
      })
      .catch(err => {
        console.error(err);
      });
  }
};
</script>
