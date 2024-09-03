<template>
  <div class="container-fluid vh-100 d-flex flex-column">

    <div class="d-flex justify-content-between align-items-center p-3">
      <ShowTitleAndCondition :title="'搜索'" :totalAnime=totalAnime />
    </div>

    <ShowLoadingCondition :loading=loading :errorMessage=errorMessage />
    <div v-if="!loading && !errorMessage && totalAnime === 0" class="alert alert-primary d-flex w-100">
      <strong>什么都没有找到...</strong>
    </div>

    <!-- 主体部分 -->
    <div class="flex-fill d-flex flex-column justify-content-center align-items-center">
      <AnimeList :data=data />
      <Paginate :totalPage=totalPage :changePage=getData />
    </div>

  </div>
</template>

<script setup>
import {ref, onMounted, watch, getCurrentInstance} from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

import Paginate from "@/component/Paginate.vue";
import ShowLoadingCondition from "@/component/ShowLoadingCondition.vue";
import AnimeList from "@/component/AnimeList.vue";
import ShowTitleAndCondition from "@/component/ShowTitleAndCondition.vue";

const { proxy } = getCurrentInstance();
const baseUrl = proxy?.$BASE_API_URL;

// 获取参数
const route = useRoute();
const keyword = ref(route.params.keyword);

watch(() => route.params.keyword, (newKeyword) => {
  keyword.value = newKeyword;
  getData(1);
});

// 定义数据信息
const totalAnime = ref(0)
const totalPage = ref(0)

// 定义数据状态
const data = ref([]);
const loading = ref(false);

// 定义错误信息
const errorMessage = ref('');

async function getData(page) {
  loading.value = true;

  // 清空数据
  errorMessage.value = ''
  data.value = [];
  totalAnime.value = 0
  totalPage.value = 0

  try {
    const response = await axios.get(baseUrl+`/anime/search?keyword=${keyword.value}&page=${page}`);
    data.value = response.data.data;
    totalAnime.value = response.data['total'];
    totalPage.value = response.data['total_page'];
  } catch (error) {
    // 处理错误
    console.error('Error fetching data:', error);
    errorMessage.value = error.message;
  }

  loading.value = false;
}

onMounted(() => {
  getData(1);
});
</script>

<style scoped>

</style>