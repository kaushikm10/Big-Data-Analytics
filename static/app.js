fetch('/view')
  .then(response => response.json())
  .then(data => {
    Highcharts.chart('container', {
      title: {
        text: 'Candlestick Chart Example'
      },
      xAxis: {
        type: 'datetime'
      },
      yAxis: {
        title: {
          text: 'Price'
        }
      },
      series: [{
        type: 'candlestick',
        name: 'AAPL',
        data: data,
        tooltip: {
          valueDecimals: 2
        }
      }]
    });
  });
