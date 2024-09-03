<template>
  <div class="container-fluid vh-100 d-flex flex-column">
    <div class="container-fluid p-3">
      <div class="row justify-content-between align-items-center">
        <div class="col-12 col-md-4 mb-3 mb-md-0">
          <ShowTitleAndCondition :title="'排名'" :totalAnime=totalAnime />
        </div>
        <div class="col-12 col-md-4" style="min-width: 300px">
          <div class="input-group">
            <select v-model="selectedSeason" class="form-select">
              <option value="all">所有时间</option>
              <option v-for="option in seasonOptions" :value="option.value" :key="option.value">
                {{ option.label }}
              </option>
            </select>
            <input v-model="numberInput" type="number" class="form-control" placeholder="最少投票人数">
            <button @click="confirm(1)" class="btn btn-primary">确认</button>
          </div>
        </div>
      </div>
    </div>

    <ShowLoadingCondition :loading=loading :errorMessage=errorMessage />

    <!-- 主体部分 -->
    <div class="flex-fill d-flex flex-column justify-content-center align-items-center">
      <AnimeList :data=data />
      <Paginate :totalPage=totalPage :changePage=confirm />
    </div>
  </div>
</template>

<script setup>
import {getCurrentInstance, onMounted, ref} from 'vue';
import axios from 'axios';

import Paginate from "@/component/Paginate.vue";
import ShowLoadingCondition from "@/component/ShowLoadingCondition.vue";
import AnimeList from "@/component/AnimeList.vue";
import ShowTitleAndCondition from "@/component/ShowTitleAndCondition.vue";


const { proxy } = getCurrentInstance();
const baseUrl = proxy?.$BASE_API_URL;

// 定义输入框的值
const numberInput = ref(1000);
const selectedSeason = ref(null);
const seasonOptions = ref([]);

// 定义数据信息
const totalAnime = ref(0)
const totalPage = ref(0)

// 定义数据状态
const data = ref([]);
const loading = ref(false);

// 定义错误信息
const errorMessage = ref('');

// 获取季节
const getSeason = (month) => {
  if (month >= 1 && month <= 3) return '冬季';
  if (month >= 4 && month <= 6) return '春季';
  if (month >= 7 && month <= 9) return '夏季';
  if (month >= 10 && month <= 12) return '秋季';
};

// 获取季节索引
const getSeasonIndex = (season) => {
  switch (season) {
    case '冬季': return 0;
    case '春季': return 1;
    case '夏季': return 2;
    case '秋季': return 3;
    default: return -1;
  }
};

const getSeasonLetter = (season) => {
  switch (season) {
    case '冬季': return 'D';
    case '春季': return 'C';
    case '夏季': return 'X';
    case '秋季': return 'Q';
  }
}

const generateSeasonOptions = () => {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const currentSeason = getSeason(currentMonth);

  // seasonOptions.value.push();

  // 从 2023 年开始生成选项，直到当前年份
  for (let year = 2023; year <= currentYear; year++) {
    for (let season of ['冬季', '春季', '夏季', '秋季']) {
      const label = `${year}${season}`;
      const value = `${year % 100}${getSeasonLetter(season)}`;

      // 如果是当前年份并且超过当前季节，则不再生成
      if (year === currentYear && getSeasonIndex(season) > getSeasonIndex(currentSeason)) {
        break;
      }

      seasonOptions.value.push({ value, label });
    }
  }

  // 设置默认值为当前季节
  const currentValue = `${currentYear % 100}${getSeasonLetter(currentSeason)}`;
  selectedSeason.value = currentValue;
};

// 确认按钮点击事件
async function confirm(page) {
  loading.value = true;

  // 清空数据
  errorMessage.value = ''
  data.value = [];
  totalAnime.value = 0
  totalPage.value = 0

  if (!numberInput.value) {
    numberInput.value = 0
  }



  try {
    if (selectedSeason.value === 'all') {
      var url = baseUrl+`/anime/list?page=${page}&min_vote=${numberInput.value}`
    } else {
      var url = baseUrl+`/anime/season?page=${page}&min_vote=${numberInput.value}&season=${selectedSeason.value}`
    }

    const response = await axios.get(url);

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
  generateSeasonOptions();
  await confirm(1);
});
</script>

<!--<style scoped>-->
<!--.d-flex {-->
<!--  flex-wrap: nowrap;-->
<!--}-->

<!--/* 小屏设备样式 */-->
<!--@media (max-width: 600px) {-->
<!--  .d-flex {-->
<!--    flex-wrap: wrap;-->
<!--  }-->

<!--  .input-group {-->
<!--    margin-top: 1rem; /* 根据需要调整间距 */-->
<!--  }-->
<!--}-->
<!--</style>-->
