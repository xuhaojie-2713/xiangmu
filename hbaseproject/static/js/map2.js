(function() {
    const data_list=[{'name': '北京', 'value': 4177}, {'name': '上海', 'value': 980}, {'name': '广东', 'value': 527}, {'name': '浙江', 'value': 407}, {'name': '广东', 'value': 335}, {'name': '四川', 'value': 135}, {'name': '江苏', 'value': 120}, {'name': '湖北', 'value': 69}, {'name': '陕西', 'value': 51},  {'name': '福建', 'value': 30}, {'name': '湖南', 'value': 25}, {'name': '天津', 'value': 20}];

    var myChart = echarts.init(document.querySelector(".map .chart"));

    var option = {
    tooltip: {
        trigger: 'item',
        formatter: function(params) {
            // 根据params中的name和value属性自定义需要显示的内容
            var content = params.name + ': ' + data_list.find(item => item.name === params.name).value+"人";
            return content;
        }
    },
    visualMap: {
            show: true, // 隐藏视觉映射组件
            min: 0,
            max: Math.max(...data_list.map(function(item) {
                return item.value;
            })),
            calculable: true
    },
    series: [
        {
            name: '数据',
            type: 'map',
            mapType: 'china',
            roam: true,
            itemStyle: {
                normal: {
                    areaColor: 'rgba(20, 41, 87,0.6)',
                    borderColor: "#195BB9",
                    borderWidth: 1,
                    label: {
                        show: true,
                        textStyle: {
                            color: 'black'
                        }
                    }
                },
            },
            data:data_list,
        },

    ],
};
  // 3. 把配置项给实例对象
  myChart.setOption(option);
  // 4. 让图表跟随屏幕自动的去适应
  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();