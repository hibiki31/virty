<template>
  <v-app>
    <notifications position="bottom right" width="290px" class="pb-8">
      <template #body="props">
        <v-alert :type="props.item.type" class="text-caption ma-1" density="compact" border="start" variant="text"
          style="background-color: white"><v-alert-title class="text-subtitle-2">{{ notificationTitle(props.item) }}</v-alert-title>
          <div data-testid="notification-body">{{ notificationBody(props.item) }}</div>
        </v-alert>
      </template>
    </notifications>
    <router-view />
  </v-app>
</template>

<script lang="ts" setup>
import {
  formatNotificationBody,
  formatNotificationTitle,
  type NotificationPayload,
} from '@/composables/notify'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function notificationPayload(item: unknown): NotificationPayload | null {
  if (!isRecord(item) || !isRecord(item.data)) return null
  const { content, title } = item.data
  if (!isRecord(title) || title.kind !== 'translation' || !isRecord(content)) return null
  if (!['api-error', 'raw-text', 'translation'].includes(String(content.kind))) return null
  return item.data as NotificationPayload
}

function notificationTitle(item: unknown): string {
  const payload = notificationPayload(item)
  if (payload) return formatNotificationTitle(payload)
  return isRecord(item) && typeof item.title === 'string' ? item.title : ''
}

function notificationBody(item: unknown): string {
  const payload = notificationPayload(item)
  if (payload) return formatNotificationBody(payload)
  return isRecord(item) && typeof item.text === 'string' ? item.text : ''
}
</script>

<style>
.font-mono {
  font-family: monospace;
}
</style>
