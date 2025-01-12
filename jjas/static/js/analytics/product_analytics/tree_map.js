const mainTreeOptions = {
    series: [
    {
      data: [
        {
          x: 'MX - Wipers',
          y: 218
        },
        {
          x: 'MFC - Oil Filters',
          y: 149
        },
        {
          x: 'MC - Cabin Filters',
          y: 184
        },
        {
          x: 'MK - Brake Shoe',
          y: 55
        },
        {
          x: 'MBB - Caliper Kits',
          y: 84
        },
        {
          x: 'MIP - Idlers',
          y: 31
        },
        {
          x: 'MF - CV boots',
          y: 70
        },
        {
          x: 'MIP - Idlers',
          y: 30
        },
        {
          x: 'MB - Ball Joint',
          y: 44
        },
      ]
    }
  ],
    legend: {
    show: false
  },
  chart: {
    height: 250,
    type: 'treemap'
  },
  colors: [
    '#3B93A5',
    '#F7B844',
    '#ADD8C7',
    '#EC3C65',
    '#CDD7B6',
    '#C1F666',
    '#D43F97',
    '#1E5D8C',
    '#421243',
    '#7F94B0',
    '#EF6537',
    '#C0ADDB'
  ],
  plotOptions: {
    treemap: {
      distributed: true,
      enableShades: true
    }
  }
  };

  var treeMapChart = new ApexCharts(document.getElementById("tree-map-chart"), mainTreeOptions);
  treeMapChart.render();