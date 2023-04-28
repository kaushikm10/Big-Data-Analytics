import { Line } from 'react-chartjs-2';
const [chartData, setChartData] = useState({});
const getData = async () => {
  const response = await fetch('your-python-data-endpoint');
  const data = await response.json();
  const labels = data.map((item) => item.label);
  const values = data.map((item) => item.value);
  setChartData({
    labels,
    datasets: [
      {
        label: 'Your Chart Title',
        data: values,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  });
};
useEffect(() => {
  getData();
}, []);
return (
  <div>
    <Line data={chartData} />
  </div>
);
