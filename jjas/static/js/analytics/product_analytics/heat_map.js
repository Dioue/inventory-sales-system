const generateData = (count, range) => {
    const data = [];
    for (let i = 0; i < count; i++) {
      data.push(Math.floor(Math.random() * (range.max - range.min + 1)) + range.min);
    }
    return data;
  }
  

var heatMapChartOptions = {
    series: [{
        name: 'MX',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MFC',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MC',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MK',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MBB',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MIP',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MF',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      },
      {
        name: 'MB',
        data: generateData(12, {
          min: 0,
          max: 90
        })
      }
      ],
        chart: {
        height: 250,
        type: 'heatmap',
        toolbar: {
            show: true,
            tools: {
                zoom: false,
                zoomin: false,
                zoomout: false,
                pan: false,
            },
        },
      },
      dataLabels: {
        enabled: false
      },
      colors: ["#008FFB"],
  };

  var heatMapChart = new ApexCharts(document.querySelector("#heat-map-chart"), heatMapChartOptions);
  heatMapChart.render();