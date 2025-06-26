<template>
  <v-btn color="info" prepend-icon="mdi-file-document-outline" text="Open Docs" class="text-none mb-3" size="small"
    variant="tonal" @click="openInNewTab"></v-btn>
</template>

<script setup lang="ts">

function openInNewTab(): void {
  // 第 3 引数でセキュリティ関連のオプションを渡す
  const newWindow = window.open(props.url, "_blank", "noopener,noreferrer");

  // 一部ブラウザでは上記フラグが効かない場合があるため明示的に null を代入
  if (newWindow) {
    newWindow.opener = null;
  }
}

const props = defineProps({
  url: {
    type: String,
    required: false,
  }
})

</script>
