<template>
  <div class="NodeDetail">
    <v-card
    class="mx-auto"
    tile
  >
    <v-simple-table dense>
      <template v-slot:default>
        <thead>
          <tr>
            <th class="text-left">name</th>
            <th class="text-left">size</th>
            <th class="text-left">model</th>
            <th class="text-left">serial</th>
            <th class="text-left">host</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, key) in get_devices()" :key="key">
            <td>{{ key }}</td>
            <td>{{ item.size }}</td>
            <td>{{ item.model }}</td>
            <td>{{ item.serial }}</td>
            <td>{{ item.host }}</td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </v-card>
  </div>
</template>

<script>
import axios from '@/axios/index';

export default {
  name: 'NodeDetail',
  components: {
  },
  data: () => ({
    facts_data: {
      ansible_facts: {
        ansible_devices: [],
        ansible_interfaces: []
      }
    }
  }),
  async mounted() {
    this.reload();
  },
  methods: {
    reload() {
      axios
        .get(`/api/nodes/${this.$route.params.name}/facts`)
        .then((res) => {
          this.facts_data= res.data;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    get_devices() {
      const devices = Object.entries(this.facts_data.ansible_facts.ansible_devices);
      devices.sort(function(p1, p2) {
        if (p1[0] < p2[0]) { return -1; }
        if (p1[0] > p2[0]) { return 1; }
        return 0;
      });
      return Object.fromEntries(devices);
    }
  }
};
</script>
