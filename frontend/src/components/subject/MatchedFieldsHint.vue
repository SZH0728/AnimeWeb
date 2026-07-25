<script setup lang="ts">
import type { MatchedFieldName } from '@/api/api-contract';

const fieldLabels: Readonly<Record<MatchedFieldName, string>> = {
  name: '原名',
  translation: '译名',
  aliases: '别名',
};

defineProps<{
  matchedFields: readonly MatchedFieldName[];
}>();
</script>

<template>
  <p v-if="matchedFields.length > 0" class="flex flex-wrap items-center gap-1 text-sm opacity-75">
    <span>匹配字段：</span>
    <span v-for="field in matchedFields" :key="field" class="badge badge-sm">{{
      fieldLabels[field]
    }}</span>
  </p>
</template>
