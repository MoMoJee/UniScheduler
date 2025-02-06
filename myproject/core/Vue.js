import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';

export default {
    mounted() {
        const calendar = new Calendar(this.$refs.fullcalendar, {
            plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
            initialView: 'dayGridMonth', // 初始视图
            locale: 'zh-cn', // 语言设置
            editable: true, // 允许编辑事件
            selectable: true, // 允许选择日期
            events: [
                // 事件数据
                { title: '事件1', start: '2024-02-07' },
                { title: '事件2', start: '2024-02-08', end: '2024-02-09' },
            ],
            eventClick: this.handleEventClick, // 事件点击处理
            dateClick: this.handleDateClick, // 日期点击处理
        });
        calendar.render();
    },
    methods: {
        handleEventClick(event) {
            console.log('Event clicked', event);
        },
        handleDateClick(date) {
            console.log('Date clicked', date);
        },
    },
};