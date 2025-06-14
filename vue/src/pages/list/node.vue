<template>
  <v-card>
    <v-card-actions>
      <v-btn prepend-icon="mdi-file-key" variant="flat" color="primary">KEY</v-btn>
      <v-btn prepend-icon="mdi-server-plus" variant="flat" color="primary">JOIN</v-btn>
      <v-btn prepend-icon="mdi-server-remove" variant="flat" color="error">LEAVE</v-btn>
    </v-card-actions>
    <v-data-table :items="items" :loading="loading" :items-per-page="10" density="comfortable">
    </v-data-table>
  </v-card>
</template>

<script setup>


const loading = ref(false)
import { ref } from 'vue'

const selected = ref([])
const items = [
  {
    name: '🍎 Apple',
    location: 'Washington',
    height: '0.1',
    base: '0.07',
    volume: '0.0001',
  },
  {
    name: '🍌 Banana',
    location: 'Ecuador',
    height: '0.2',
    base: '0.05',
    volume: '0.0002',
  },
  {
    name: '🍇 Grapes',
    location: 'Italy',
    height: '0.02',
    base: '0.02',
    volume: '0.00001',
  },
  {
    name: '🍉 Watermelon',
    location: 'China',
    height: '0.4',
    base: '0.3',
    volume: '0.03',
  },
  {
    name: '🍍 Pineapple',
    location: 'Thailand',
    height: '0.3',
    base: '0.2',
    volume: '0.005',
  },
  {
    name: '🍒 Cherries',
    location: 'Turkey',
    height: '0.02',
    base: '0.02',
    volume: '0.00001',
  },
  {
    name: '🥭 Mango',
    location: 'India',
    height: '0.15',
    base: '0.1',
    volume: '0.0005',
  },
  {
    name: '🍓 Strawberry',
    location: 'USA',
    height: '0.03',
    base: '0.03',
    volume: '0.00002',
  },
  {
    name: '🍑 Peach',
    location: 'China',
    height: '0.09',
    base: '0.08',
    volume: '0.0004',
  },
  {
    name: '🥝 Kiwi',
    location: 'New Zealand',
    height: '0.05',
    base: '0.05',
    volume: '0.0001',
  },
]

</script>
