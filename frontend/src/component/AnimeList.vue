<template>
  <div>
    <router-link
        :to="'/anime/'+anime.id"
        v-for="anime in filteredData"
        :key="anime.id">

      <div class="card mb-3" :style="{ maxWidth: '900px', border: '1px solid #b3e5fc', backgroundColor: 'white' }">
        <div class="row g-0">

          <!-- 图片 -->
          <div class="col-md-4 d-flex justify-content-center">
            <img :src="anime.picture" class="img-fluid rounded-start card-img-top" :alt="anime.name" />
          </div>

          <!-- 数据展示 -->
          <div class="col-md-8">
            <div class="card-body">

              <!-- 标题与评分投票 -->
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h5 class="card-title">{{ anime.name }}</h5>
                <div class="d-flex align-items-center">
                  <span class="badge bg-light text-dark me-2">{{ anime.score }}</span>
                  <span class="badge bg-light text-dark">{{ anime.vote }} 票</span>
                </div>
              </div>

              <!--  译名 -->
              <p class="card-text text-secondary">{{ anime.translation }}</p>

              <!-- 标签 -->
              <div v-if="anime.tag.length">
                <span v-for="tag in anime.tag" :key="tag" class="badge bg-light text-dark tag">{{ tag }}</span>
              </div>

              <!-- 简介 -->
              <p class="card-text">{{ anime.description }}</p>

            </div>
          </div>

        </div>
      </div>
    </router-link>
  </div>
</template>

<script setup>
import {computed, defineProps} from 'vue';

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

// 过滤空数据
const filteredData = computed(() => props.data.filter(item => item));
</script>

<style scoped>
a {
  text-decoration: none;
  color: inherit;
}

.tag {
  margin: 2px;
}

.card-img-top {
  max-width: 300px;
  height: auto;
  object-fit: contain;
}
</style>
