// Get labels and data from the template
let spending_element = document.getElementById("id_spending_data");
let original_spending_data = JSON.parse(spending_element.textContent);

console.log(original_spending_data);

// Filter data based on date
// function filterDataByDate(data, startDate, endDate) {
//   return data.filter((transaction) => {
//     let transactionDate = new Date(transaction.date);
//     return transactionDate >= startDate && transactionDate <= endDate;
//   });
// }

function filterDataByDate(data, startDate, endDate) {
  let filteredData = data.filter((transaction) => {
    let transactionDate = new Date(transaction.date);
    return transactionDate >= startDate && transactionDate <= endDate;
  });

  console.log("Filtered Data:", filteredData);

  return filteredData;
}

// Function to update the chart based on the selected time range
function updateChart(selectedRange) {
  let filtered_transactions;

  // Set start and end dates based on the selected time range
  let today = new Date();
  let startDate, endDate;

  switch (selectedRange) {
    case "today":
      startDate = new Date(today).setHours(0, 0, 0, 0);
      endDate = new Date(today);
      break;

    case "weekly":
      startDate = new Date(today.setDate(today.getDate() - today.getDay()));
      endDate = new Date(today.setDate(today.getDate() + 6));
      break;

    case "monthly":
      startDate = new Date(today.getFullYear(), today.getMonth(), 1);
      endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      break;

    case "yearly":
      startDate = new Date(today.getFullYear(), 0, 1);
      endDate = new Date(today.getFullYear(), 11, 31);
      break;

    default:
      startDate = new Date(+0);
      endDate = new Date(today.getFullYear() + 10, 11, 31);
      break;
  }

  // Filter spending_data based on date
  filtered_transactions = filterDataByDate(
    original_spending_data,
    startDate,
    endDate
  );

  let totalIncome = filtered_transactions
    .filter((transaction) => transaction.income_or_expense === "Income")
    .reduce((sum, transaction) => sum + parseFloat(transaction.amount), 0);

  let totalExpense = filtered_transactions
    .filter((transaction) => transaction.income_or_expense === "Expense")
    .reduce((sum, transaction) => sum + parseFloat(transaction.amount), 0);

  // Update chart
  myChart.data.datasets[0].data = [totalIncome, totalExpense];

  myChart.update();
}

// Initial totals
function calculateInitialTotals(data) {
  let totalIncome = data
    .filter((transaction) => transaction.income_or_expense === "Income")
    .reduce((sum, transaction) => sum + parseFloat(transaction.amount), 0);

  let totalExpense = data
    .filter((transaction) => transaction.income_or_expense === "Expense")
    .reduce((sum, transaction) => sum + parseFloat(transaction.amount), 0);

  return { totalIncome, totalExpense };
}

let initialTotals = calculateInitialTotals(original_spending_data);

// Setup chart
let ctx = document.getElementById("budgetChart").getContext("2d");

let myChart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: ["Income", "Expense"],
    datasets: [
      {
        data: [initialTotals.totalIncome, initialTotals.totalExpense],
        backgroundColor: ["rgba(78, 159, 61, 0.3)", "rgba(215, 35, 35, 0.3)"],
        borderColor: ["rgba(78, 159, 61, 1)", "rgba(215, 35, 35, 1)"],
        borderWidth: 8,
        label: [
          "€" + initialTotals.totalIncome,
          "€" + initialTotals.totalExpense,
        ],
      },
    ],
  },
  options: {
    plugins: {
      legend: {
        display: true,
        labels: {
          font: {
            size: 16,
          },
          generateLabels: function (chart) {
            return [
              {
                text: "Income",
                fillStyle: "rgba(78, 159, 61, 0.3)",
                strokeStyle: "rgba(78, 159, 61, 1)",
                fontColor: "lightgrey",
                lineWidth: 4,
              },
              {
                text: "Expense",
                fillStyle: "rgba(215, 35, 35, 0.3)",
                strokeStyle: "rgba(215, 35, 35, 1)",
                lineWidth: 4,
              },
            ];
          },
        },
      },
      tooltip: {
        display: false,
      },
    },
    responsive: false,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        display: false,
      },
      x: {
        display: false,
      },
    },
    animation: {
      onComplete: function (animation) {
        let ctx = myChart.ctx;

        myChart.data.datasets.forEach(function (dataset) {
          for (let i = 0; i < dataset.data.length; i++) {
            let total = dataset.data[i];

            ctx.fillStyle = "lightgrey";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "24px Josefin Sans";

            let x = myChart.getDatasetMeta(0).data[i].x;
            let y = myChart.getDatasetMeta(0).data[i].y + 40;

            ctx.fillText("€" + total.toFixed(2), x, y);
          }
        });
      },
    },
  },
});

// Select eventListener
document
  .getElementById("timeRangeSelect")
  .addEventListener("change", function () {
    let selectedRange = this.value;

    // Update chart based on range
    updateChart(selectedRange);
  });
