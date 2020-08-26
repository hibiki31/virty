<template>
  <div class="QueueDetail">
    <p class="title">
      <v-icon>mdi-desktop-classic</v-icon>
      {{ queData.id }}
    </p>
    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            Parameter
          </v-card-title>
          <v-list class="body-2" dense>
            <v-list-item>
              <v-list-item-content>Host</v-list-item-content>
              <v-list-item-content class="align-end">{{ queData.resource }}</v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-content>Node</v-list-item-content>
              <v-list-item-content class="align-end">{{ queData.object }}</v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-content>VNC Port</v-list-item-content>
              <v-list-item-content class="align-end">{{ queData.method }}</v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-content>Protein:</v-list-item-content>
              <v-list-item-content class="align-end">{{ queData.userId }}</v-list-item-content>
            </v-list-item>

          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <v-card>
          <v-card-title class="subheading font-weight-bold">Send JSON</v-card-title>
          <v-card-text>{{queData.json}}</v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="6">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            <v-icon>mdi-transit-connection-variant</v-icon>Error log
          </v-card-title>
          <v-card-text style="white-space:pre-wrap; word-wrap:break-word;">{{errLog}}</v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="6">
        <v-card>
          <v-card-title class="subheading font-weight-bold">
            <v-icon>mdi-transit-connection-variant</v-icon>Stand log
          </v-card-title>
          <v-card-text style="white-space:pre-wrap; word-wrap:break-word;">{{outLog}}</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from '@/axios/index';

export default {
  name: 'QueueDetail',
  data: () => ({
    errLog: '',
    outLog: '',
    queData: {}
  }),
  async mounted() {
    const uuid = `${this.$route.params.uuid}`;
    await axios
      .get('/api/queue/' + uuid)
      .then((response) => (this.queData = response.data));
    await axios
      .get('/api/queue/' + uuid + '/log/out', { responseType: 'text' })
      .then((response) => (this.outLog = response.data));
    await axios
      .get('/api/queue/' + uuid + '/log/err', { responseType: 'text' })
      .then((response) => (this.errLog = response.data));
  }
};
</script>
