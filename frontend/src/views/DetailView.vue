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
const web = ref({})
const loading = ref(false);

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

    response = await axios.get(baseUrl+'/anime/webinfo');
    web.value = response.data;
  } catch (error) {
    // 处理错误
    console.error('Error fetching data:', error);
    errorMessage.value = error.message;
  }

  loading.value = false;
}

function addValueToDataset(value) {
  value.fill = false;
  value.showLine = true;
  value.borderWidth = 1;
  return value
}

function drawChart(data, webInfo) {
  const scoreCanvasChart = document.getElementById('scoreChartCanvas');
  const voteCanvasChart = document.getElementById('voteChartCanvas');

  const labels = [];
  let bangumiScoreDataset = [];
  let bangumiVoteDataset = [];
  let anikoreScoreDataset = [];
  let anikoreVoteDataset = [];
  let anidbScoreDataset = [];
  let anidbVoteDataset = [];
  let myAnimeListScoreDataset = [];
  let myAnimeListVoteDataset = [];
  let sumScoreDataset = [];
  let sumVoteDataset = [];

  for (let i = 0; i < data.length; i++) {
    const childData = data[i];
    labels.push(childData.date);

    let hasInsertBangumiData = false;
    let hasInsertAnikoreData = false;
    let hasInsertAnidbData = false;
    let hasInsertMyAnimeListData = false;

    for (const key in childData.detailScore) {
      if (childData.detailScore.hasOwnProperty(key)) {
        const innerScores = childData.detailScore[key];
        const webName = webInfo[key];

        if (webName === 'Bangumi') {
          bangumiScoreDataset.push(innerScores.score);
          bangumiVoteDataset.push(innerScores.vote);
          hasInsertBangumiData = true;
        } else if (webName === 'Anikore') {
          anikoreScoreDataset.push(innerScores.score);
          anikoreVoteDataset.push(innerScores.vote);
          hasInsertAnikoreData = true;
        } else if (webName === 'Anidb') {
          anidbScoreDataset.push(innerScores.score);
          anidbVoteDataset.push(innerScores.vote);
          hasInsertAnidbData = true;
        } else if (webName === 'MyAnimeList') {
          myAnimeListScoreDataset.push(innerScores.score);
          myAnimeListVoteDataset.push(innerScores.vote);
          hasInsertMyAnimeListData = true;
        }
      }
    }

    if (!hasInsertBangumiData) {
      bangumiScoreDataset.push(null);
      bangumiVoteDataset.push(null);
    }

    if (!hasInsertAnikoreData) {
      anikoreScoreDataset.push(null);
      anikoreVoteDataset.push(null);
    }

    if (!hasInsertAnidbData) {
      anidbScoreDataset.push(null);
      anidbVoteDataset.push(null);
    }

    if (!hasInsertMyAnimeListData) {
      myAnimeListScoreDataset.push(null);
      myAnimeListVoteDataset.push(null);
    }

    sumScoreDataset.push(childData.score);
    sumVoteDataset.push(childData.vote);
  }

  bangumiScoreDataset = addValueToDataset({
    label: 'bangumiScore',
    data: bangumiScoreDataset,
    backgroundColor: 'rgba(255,182,193)',
    borderColor: 'rgba(255,182,193)',
  });

  bangumiVoteDataset = addValueToDataset({
    label: 'bangumiVote',
    data: bangumiVoteDataset,
    backgroundColor: 'rgba(255,182,193)',
    borderColor: 'rgba(255,182,193)',
  });

  anikoreScoreDataset = addValueToDataset({
    label: 'anikoreScore',
    data: anikoreScoreDataset,
    backgroundColor: 'rgb(255,221,0)',
    borderColor: 'rgb(255,221,0)',
  });

  anikoreVoteDataset = addValueToDataset({
    label: 'anikoreVote',
    data: anikoreVoteDataset,
    backgroundColor: 'rgb(255,221,0)',
    borderColor: 'rgb(255,221,0)',
  });

  anidbScoreDataset = addValueToDataset({
    label: 'anidbScore',
    data: anidbScoreDataset,
    backgroundColor: 'rgba(169,169,169)',
    borderColor: 'rgba(169,169,169)',
  });

  anidbVoteDataset = addValueToDataset({
    label: 'anidbVote',
    data: anidbVoteDataset,
    backgroundColor: 'rgba(169,169,169)',
    borderColor: 'rgba(169,169,169)',
  });

  myAnimeListScoreDataset = addValueToDataset({
    label: 'myAnimeListScore',
    data: myAnimeListScoreDataset,
    backgroundColor: 'rgba(65,105,225)',
    borderColor: 'rgba(65,105,225)',
  });

  myAnimeListVoteDataset = addValueToDataset({
    label: 'myAnimeListVote',
    data: myAnimeListVoteDataset,
    backgroundColor: 'rgba(65,105,225)',
    borderColor: 'rgba(65,105,225)',
  });

  sumScoreDataset = addValueToDataset({
    label: 'sumScore',
    data: sumScoreDataset,
    backgroundColor: 'rgba(144,238,144)',
    borderColor: 'rgba(144,238,144)',
  });

  sumVoteDataset = addValueToDataset({
    label: 'sumVote',
    data: sumVoteDataset,
    backgroundColor: 'rgba(144,238,144)',
    borderColor: 'rgba(144,238,144)',
  });

  let scoreChart = new Chart(scoreCanvasChart, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        bangumiScoreDataset,
        anikoreScoreDataset,
        anidbScoreDataset,
        myAnimeListScoreDataset,
        sumScoreDataset
      ]
    }
  })

  let voteChart = new Chart(voteCanvasChart, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        bangumiVoteDataset,
        anikoreVoteDataset,
        anidbVoteDataset,
        myAnimeListVoteDataset,
        sumVoteDataset
      ]
    }
  })

}

async function getData(id) {
  await getDetail(id)
  await getScoreHistory(id)
  drawChart(scores.value, web.value)
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