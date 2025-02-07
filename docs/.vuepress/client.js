import { defineClientConfig } from 'vuepress/client'
import PostList from "./components/PostList.vue";
import CustomLayout from "./theme/layouts/CustomLayout.vue";
import LogList from "./components/LogList.vue";
import BookList from "./components/BookList.vue";
import Footer from "./theme/Footer.vue";
import Header from "./theme/Header.vue";
import Home from "./components/home/Home.vue";

export default defineClientConfig({
    enhance({ app, router, siteData }) {
        app.component('Home', Home)
        app.component('PostList', PostList)
        app.component('LogList', LogList)
        app.component('BookList', BookList)
        app.component('Footer', Footer)
        app.component('Header', Header)
    },
    layouts: {
        CustomLayout,
    },
    setup() {},
    rootComponents: [],
})
