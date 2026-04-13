import { defineClientConfig } from 'vuepress/client'
import PostList from "./components/PostList.vue";
import CustomLayout from "./theme/layouts/CustomLayout.vue";
import LogList from "./components/LogList.vue";
import BookList from "./components/BookList.vue";
import StudyList from "./components/StudyList.vue";
import Footer from "./theme/Footer.vue";
import Header from "./theme/Header.vue";
import Home from "./components/home/Home.vue";
import ResumeCover from "./components/resume/ResumeCover.vue";

export default defineClientConfig({
    enhance({ app, router }) {
        app.component('Home', Home)
        app.component('PostList', PostList)
        app.component('LogList', LogList)
        app.component('BookList', BookList)
        app.component('StudyList', StudyList)
        app.component('Footer', Footer)
        app.component('Header', Header)
        app.component('ResumeCover', ResumeCover)

        if (typeof window !== 'undefined') {
            const loadMermaid = () => {
                if (window.mermaid) {
                    window.mermaid.run({ querySelector: 'pre.mermaid' })
                    return
                }
                const script = document.createElement('script')
                script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js'
                script.onload = () => {
                    window.mermaid.initialize({ startOnLoad: false, theme: 'default' })
                    window.mermaid.run({ querySelector: 'pre.mermaid' })
                }
                document.head.appendChild(script)
            }
            router.afterEach(() => {
                setTimeout(loadMermaid, 100)
            })
        }
    },
    layouts: {
        CustomLayout,
    },
    setup() {},
    rootComponents: [],
})
