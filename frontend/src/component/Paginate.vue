
<template>
  <nav aria-label="Page navigation example" v-if="totalPage !== 1">
    <ul class="pagination">
      <li class="page-item" :class="{ disabled: currentPage === 1 }">
        <button class="page-link" href="#" @click.prevent="changeConfirmPage(1)">首页</button>
      </li>
      <li class="page-item" :class="{ disabled: currentPage === 1 }">
        <button class="page-link" href="#" @click.prevent="changeConfirmPage(currentPage - 1)">上一页</button>
      </li>
      <!-- 显示前导省略号 -->
      <li v-if="currentPage > 4" class="page-item">
        <button class="page-link" disabled>...</button>
      </li>
      <!-- 显示具体页数 -->
      <li class="page-item" v-for="page in visiblePages" :key="page" :class="{ active: currentPage === page }">
        <button class="page-link" href="#" @click.prevent="changeConfirmPage(page)">{{ page }}</button>
      </li>
      <!-- 显示尾随省略号 -->
      <li v-if="currentPage < totalPage - 3" class="page-item">
        <button class="page-link" disabled>...</button>
      </li>
      <li class="page-item" :class="{ disabled: currentPage === totalPage }">
        <button class="page-link" href="#" @click.prevent="changeConfirmPage(currentPage + 1)">下一页</button>
      </li>
      <li class="page-item" :class="{ disabled: currentPage === totalPage }">
        <button class="page-link" href="#" @click.prevent="changeConfirmPage(totalPage)">尾页</button>
      </li>
    </ul>

    <!-- 添加跳转到指定页的功能 -->
    <div class="input-group mt-3" style="max-width: 600px">
      <input type="number" class="form-control" placeholder="跳转到第几页" v-model="gotoPage" @keyup.enter="jumpToPage">
      <button class="btn btn-primary" type="button" @click="jumpToPage">跳转</button>
    </div>
  </nav>
</template>

<script setup>
import {ref, defineProps, computed} from "vue";

const props = defineProps({totalPage: Number, changePage: Function})

const currentPage = ref(1);
const gotoPage = ref('');

async function changeConfirmPage(page) {
  if (page >= 1 && page <= props.totalPage && page !== currentPage.value) {
    currentPage.value = page;
    await props.changePage(page);
  }
}

const visiblePages = computed(() => {
  const start = Math.max(currentPage.value - 2, 1);
  const end = Math.min(currentPage.value + 2, props.totalPage);

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});

function jumpToPage() {
  const pageNumber = parseInt(gotoPage.value, 10);
  if (!isNaN(pageNumber) && pageNumber >= 1 && pageNumber <= props.totalPage) {
    changeConfirmPage(pageNumber);
    gotoPage.value = ''; // 清空输入框
  } else {
    alert('请输入有效的页码！');
  }
}
</script>

<style scoped>

</style>