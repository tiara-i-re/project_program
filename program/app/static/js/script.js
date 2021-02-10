

var win_per = Number(document.getElementById( 'win' ).title);
var draw_per = Number(document.getElementById( 'draw' ).title);
var lose_per = Number(document.getElementById( 'lose' ).title);

var ctx = document.getElementById("myChart");

var myChart = new Chart(ctx,
{
  type: "doughnut",
  data: {
    labels: ["Win", "Draw", "Lose"],
    datasets: [
      {
        data: [win_per, draw_per, lose_per],
        backgroundColor: [
          "springgreen",
          "aliceblue",
          "rgb(255, 99, 132)"
        ]
      }],
  },
  options: {

        responsive: false,
        plugins: {
            datalabels: {
                color: "#000",
                font: {
                    weight: 'bold',
                    size: 20,
                },
                formatter: (value, ctx) => {
                    let label = ctx.chart.data.labels[ctx.dataIndex];
                    return label + '\n' + value + '%';
                }
                }
            }
    }
});
