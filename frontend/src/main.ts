import { createApp, h } from 'vue';
import { createPinia } from 'pinia';
import { DefaultApolloClient } from '@vue/apollo-composable';

import App from './App.vue';
import router from './shared/router';
import apolloClient from './shared/api/apollo';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap';
import './styles/theme.scss';

const app = createApp({
  setup() {
    return () => h(App);
  }
});

const pinia = createPinia();

app.use(pinia);
app.use(router);
app.provide(DefaultApolloClient, apolloClient);

app.mount('#app');

