<template>
  <div class="container-fluid vh-100 d-flex flex-column">

    <div class="d-flex justify-content-between align-items-center p-3">
      <!-- 右上角标题 -->
      <div class="d-flex align-items-center">
        <h2 class="text-info">排名</h2>
        <span class="ms-2 text-secondary">(一共{{ totalAnime }}部动画)</span>
      </div>

      <!-- 左上角标题与输入框 -->
      <div class="input-group ms-3" style="width: 200px;">
        <input v-model="numberInput" type="number" class="form-control" placeholder="最少投票人数">
        <button @click="confirmNumber(1)" class="btn btn-primary">确认</button>
      </div>
    </div>

    <div v-if="loading" class="alert alert-info d-flex w-100">
      <strong>正在加载...</strong>
    </div>
    <div v-if="hasError" class="alert alert-danger d-flex w-100">
      <strong>错误!</strong> 访问数据失败: {{ errorMessage }}
    </div>

    <!-- 主体部分 -->
    <div class="flex-fill d-flex flex-column justify-content-center align-items-center">
      <div v-if="data.length !== 0">
        <router-link :to="'/anime/'+anime.id" v-for="anime in data" :key="anime.id">
          <div class="card mb-3" style="max-width: 900px; border: 1px solid #b3e5fc; background-color: white;">
            <div class="row g-0">
              <div class="col-md-4 d-flex justify-content-center">
                <img :src="anime.picture" class="img-fluid rounded-start card-img-top" alt="...">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <div class="d-flex align-items-center justify-content-between mb-2">
                    <h5 class="card-title">{{ anime.name }}</h5>
                    <div class="d-flex align-items-center">
                      <span class="badge bg-light text-dark me-2">{{ anime.score }}</span>
                      <span class="badge bg-light text-dark">{{ anime.vote }} 票</span>
                    </div>
                  </div>
                  <p class="card-text text-secondary">{{ anime.translation }}</p>
                  <div v-if="anime.tag.length !== 0">
                    <span v-for="tag in anime.tag" class="badge bg-light text-dark tag">{{ tag }}</span>
                  </div>
                  <p class="card-text">{{ anime.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </router-link>
      </div>

      <!-- 分页组件 -->
      <nav aria-label="Page navigation example">
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" href="#" @click.prevent="changePage(1)">首页</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一页</button>
          </li>
          <!-- 显示前导省略号 -->
          <li v-if="currentPage > 4" class="page-item">
            <button class="page-link" disabled>...</button>
          </li>
          <!-- 显示具体页数 -->
          <li class="page-item" v-for="page in visiblePages" :key="page" :class="{ active: currentPage === page }">
            <button class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</button>
          </li>
          <!-- 显示尾随省略号 -->
          <li v-if="currentPage < totalPage - 3" class="page-item">
            <button class="page-link" disabled>...</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPage }">
            <button class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一页</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPage }">
            <button class="page-link" href="#" @click.prevent="changePage(totalPage)">尾页</button>
          </li>
        </ul>

        <!-- 添加跳转到指定页的功能 -->
        <div class="input-group mt-3" style="max-width: 600px">
          <input type="number" class="form-control" placeholder="跳转到第几页" v-model="gotoPage" @keyup.enter="jumpToPage">
          <button class="btn btn-primary" type="button" @click="jumpToPage">跳转</button>
        </div>
      </nav>

    </div>

  </div>
</template>

<script setup>
import {ref, onMounted, computed} from 'vue';
import axios from 'axios';

// 定义输入框的值
const numberInput = ref(1000);

// 定义数据信息
const totalAnime = ref(0)
const totalPage = ref(0)

const currentPage = ref(1);
const gotoPage = ref('');

// 定义数据状态
const data = ref([]);
const loading = ref(false);

// 定义错误信息
const hasError = ref(false);
const errorMessage = ref('');

// 确认按钮点击事件
async function confirmNumber(page) {
  loading.value = true;
  hasError.value = false;

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
    hasError.value = true;
    errorMessage.value = error.message;
  }

  loading.value = false;
}

async function changePage(page) {

  if (page >= 1 && page <= totalPage.value && page !== currentPage.value) {
    currentPage.value = page;
    await confirmNumber(page);
  }
}

const visiblePages = computed(() => {
  const start = Math.max(currentPage.value - 2, 1);
  const end = Math.min(currentPage.value + 2, totalPage.value);

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});

function jumpToPage() {
  const pageNumber = parseInt(gotoPage.value, 10);
  if (!isNaN(pageNumber) && pageNumber >= 1 && pageNumber <= totalPage.value) {
    changePage(pageNumber);
    gotoPage.value = ''; // 清空输入框
  } else {
    alert('请输入有效的页码！');
  }
}

// 初始化数据
onMounted(async () => {
  await confirmNumber(1);
});
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