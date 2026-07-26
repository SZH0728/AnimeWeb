<script setup lang="ts">
import type { RankingItem } from '@/api/api-contract';
import type { RankingType } from '@/types/api-requests';

import SubjectListItem from '@/components/subject/SubjectListItem.vue';

type RankingListItemProps = Omit<RankingItem, 'subject'> & {
  subject: Omit<RankingItem['subject'], 'tags'> & {
    tags: readonly string[];
  };
};

defineProps<{
  item: RankingListItemProps;
  rankingType: RankingType;
}>();
</script>

<template>
  <SubjectListItem :subject="item.subject">
    <template #metadata>
      <span class="text-primary flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm font-medium">
        本站第 {{ item.position }} 名
      </span>
    </template>
  </SubjectListItem>
</template>
