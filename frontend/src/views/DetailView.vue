<template>
  <div style="margin-top: 20px"/>
  <ShowLoadingCondition :loading=loading :errorMessage=errorMessage />

  <div v-if="!loading && !errorMessage && !detail" class="alert alert-primary d-flex w-100">
    <strong>没有找到你所要查询的数据</strong>
  </div>

  <div class="card mb-3" style="max-width: 100%;">
    <div class="row g-0">
      <div class="col-md-4">
        <img :src="detail.picture" class="img-fluid rounded-start" alt="...">
      </div>
      <div class="col-md-8">
        <div class="card-body">
          <h5 class="card-title">{{ detail.name }}</h5>
          <p class="card-text text-secondary"> {{ detail.translation }}</p>
          <p class="card-text"><strong>别名:</strong>
            <span v-for="alia in detail.alias" :key="alia" class="badge bg-light text-black me-1">{{ alia }}</span>
          </p>
          <p class="card-text"><strong>时间:</strong> {{ detail.time }}</p>
          <p class="card-text"><strong>标签:</strong>
            <span v-for="tag in detail.tag" :key="tag" class="badge bg-light text-black me-1">{{ tag }}</span>
          </p>
          <p class="card-text"><strong>导演:</strong> {{ detail.director }}</p>
          <p class="card-text"><strong>演员:</strong>
            <span v-for="c in detail.cast" :key="c" class="badge bg-light text-black me-1">{{ c }}</span>
          </p>
          <p class="card-text"><strong>描述:</strong> {{ detail.description }}</p>
          <p class="card-text">
            <strong>来源:</strong>
            <a :href="'https://' + detail.url" class="btn btn-outline-info">{{ detail.source }}</a>
          </p>
        </div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="row">
      <div class="col-12">
        <div class="chart-container">
          <canvas id="scoreChartCanvas"></canvas>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <div class="chart-container">
          <canvas id="voteChartCanvas"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {getCurrentInstance, onMounted, ref, watch} from 'vue';
import {useRoute} from "vue-router";
import axios from 'axios';
import Chart from 'chart.js/auto';

import ShowLoadingCondition from "@/component/ShowLoadingCondition.vue";


const { proxy } = getCurrentInstance();
const baseUrl = proxy?.$BASE_API_URL;

// 获取参数
const route = useRoute();
const id = ref(route.params.id);

watch(() => route.params.id, (newId) => {
  id.value = newId;
  getData(newId);
});

// 定义数据状态
const detail = ref({});
const scores = ref([]);
const loading = ref(false);
let webInfo = localStorage.getItem('webInfo')
webInfo = JSON.parse(webInfo)
// let webInfo = null

// 定义错误信息
const errorMessage = ref('');

async function getDetail(id) {
  loading.value = true;
  errorMessage.value = ''
  try {
    const response = await axios.get(baseUrl+`/anime/detail/${id}`);
    detail.value = response.data;
  } catch (error) {
    // 处理错误
    console.error('Error fetching data:', error);
    errorMessage.value = error.message;
  }

  loading.value = false;
}

async function getScoreHistory(id) {
  loading.value = true;
  errorMessage.value = ''
  try {
    let response = await axios.get(baseUrl+`/anime/score/${id}`);
    scores.value = response.data;

    if (!webInfo){
      response = await axios.get(baseUrl+'/anime/webinfo');
      webInfo = response.data;
      localStorage.setItem('webInfo', JSON.stringify(webInfo))
    }
  } catch (error) {
    // 处理错误
    console.error('Error fetching data:', error);
    errorMessage.value = error.message;
  }

  loading.value = false;
}

function drawChart(data, webInfo) {
  const scoreCanvasChart = document.getElementById('scoreChartCanvas');
  const voteCanvasChart = document.getElementById('voteChartCanvas');

  const labels = [];
  const datasets = {
    bangumi: { score: [], vote: [] },
    anikore: { score: [], vote: [] },
    anidb: { score: [], vote: [] },
    myAnimeList: { score: [], vote: [] },
    sum: { score: [], vote: [] }
  };

  for (let i = 0; i < data.length; i++) {
    const childData = data[i];
    labels.push(childData.date);

    for (const key in childData["detailScore"]) {
      if (childData["detailScore"].hasOwnProperty(key)) {
        const innerScores = childData["detailScore"][key];
        const webName = webInfo[key];

        switch (webName) {
          case 'Bangumi':
            datasets.bangumi.score.push(innerScores.score);
            datasets.bangumi.vote.push(innerScores.vote);
            break;
          case 'Anikore':
            datasets.anikore.score.push(innerScores.score);
            datasets.anikore.vote.push(innerScores.vote);
            break;
          case 'Anidb':
            datasets.anidb.score.push(innerScores.score);
            datasets.anidb.vote.push(innerScores.vote);
            break;
          case 'MyAnimeList':
            datasets.myAnimeList.score.push(innerScores.score);
            datasets.myAnimeList.vote.push(innerScores.vote);
            break;
        }
      }
    }

    // Fill missing values with null
    const fillMissingValues = (dataset) => {
      if (datasets[dataset].score.length < i + 1) {
        datasets[dataset].score.push(null);
        datasets[dataset].vote.push(null);
      }
    };

    fillMissingValues('bangumi');
    fillMissingValues('anikore');
    fillMissingValues('anidb');
    fillMissingValues('myAnimeList');

    datasets.sum.score.push(childData.score);
    datasets.sum.vote.push(childData.vote);
  }

  const createDataset = (label, data, color) => ({
    label,
    data,
    backgroundColor: color,
    borderColor: color
  });

  const scoreDatasets = Object.keys(datasets).map((key) => {
    const color = {
      bangumi: 'rgba(255,182,193)',
      anikore: 'rgb(255,221,0)',
      anidb: 'rgba(169,169,169)',
      myAnimeList: 'rgba(65,105,225)',
      sum: 'rgba(144,238,144)'
    }[key];
    return createDataset(`${key}Score`, datasets[key].score, color);
  });

  const voteDatasets = Object.keys(datasets).map((key) => {
    const color = {
      bangumi: 'rgba(255,182,193)',
      anikore: 'rgb(255,221,0)',
      anidb: 'rgba(169,169,169)',
      myAnimeList: 'rgba(65,105,225)',
      sum: 'rgba(144,238,144)'
    }[key];
    return createDataset(`${key}Vote`, datasets[key].vote, color);
  });

  new Chart(scoreCanvasChart, {
    type: 'line',
    data: {
      labels,
      datasets: scoreDatasets
    }
  });

  new Chart(voteCanvasChart, {
    type: 'line',
    data: {
      labels,
      datasets: voteDatasets
    }
  });
}


async function getData(id) {
  await getDetail(id)
  await getScoreHistory(id)
  drawChart(scores.value, webInfo)
}

onMounted(() => {
  getData(id.value);
})

</script>

<style scoped>
.chart-container {
  width: 100%;
  height: auto;
}

.card-text strong {
  margin-right: 5px;
}
</style>