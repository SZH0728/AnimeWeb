<template>
  <div class="container-fluid vh-100 d-flex flex-column">

    <div class="d-flex justify-content-between align-items-center p-3">
      <ShowTitleAndCondition :title="'排名'" :totalAnime=totalAnime />

      <!-- 左上角标题与输入框 -->
      <div class="input-group ms-3" style="width: 200px;">
        <input v-model="numberInput" type="number" class="form-control" placeholder="最少投票人数">
        <button @click="confirmNumber(1)" class="btn btn-primary">确认</button>
      </div>
    </div>

    <ShowLoadingCondition :loading=loading :errorMessage=errorMessage />

    <!-- 主体部分 -->
    <div class="flex-fill d-flex flex-column justify-content-center align-items-center">
      <AnimeList :data=data />
      <Paginate :totalPage=totalPage :changePage=confirmNumber />
    </div>

  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import axios from 'axios';

import Paginate from "@/component/Paginate.vue";
import ShowLoadingCondition from "@/component/ShowLoadingCondition.vue";
import AnimeList from "@/component/AnimeList.vue";
import ShowTitleAndCondition from "@/component/ShowTitleAndCondition.vue";

// 定义输入框的值
const numberInput = ref(1000);

// 定义数据信息
const totalAnime = ref(0)
const totalPage = ref(0)

// 定义数据状态
const data = ref([]);
const loading = ref(false);

// 定义错误信息
const errorMessage = ref('');

// 确认按钮点击事件
async function confirmNumber(page) {
  loading.value = true;

  // 清空数据
  data.value = [];
  totalAnime.value = 0
  totalPage.value = 0

  try {
    const response = await axios.get(`http://127.0.0.1:8000/anime/list?page=${page}&min_vote=${numberInput.value}`);
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

// 初始化数据
onMounted(async () => {
  await confirmNumber(1);
});
</script>