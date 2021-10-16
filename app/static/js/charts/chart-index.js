"use strict";



document.addEventListener("DOMContentLoaded", function () {
    // ------------------------------------------------------- //
    // Charts Gradients
    // ------------------------------------------------------ //
    var canvas = document.querySelector("canvas");

    var ctx1 = canvas.getContext("2d");
    var gradient1 = ctx1.createLinearGradient(150, 0, 150, 300);
    gradient1.addColorStop(0, "rgba(133, 180, 242, 0.91)");
    gradient1.addColorStop(1, "rgba(255, 119, 119, 0.94)");

    var gradient2 = ctx1.createLinearGradient(146.0, 0.0, 154.0, 300.0);
    gradient2.addColorStop(0, "rgba(104, 179, 112, 0.85)");
    gradient2.addColorStop(1, "rgba(76, 162, 205, 0.85)");

    // ------------------------------------------------------- //
    // Line Chart
    // ------------------------------------------------------ //
    var EVENTCHART = document.getElementById("monthlyEventChart");

    var EventChart = new Chart(EVENTCHART, {
        type: "line",
        options: {
            legend: { labels: { fontColor: "#777", fontSize: 12 } },
            scales: {
                xAxes: [
                    {
                        display: true,
                        gridLines: {
                            color: "#eee",
                        },
                    },
                ],
                yAxes: [
                    {
                        display: true,
                        gridLines: {
                            color: "#eee",
                        },
                    },
                ],
            },
        },
        data: {
            labels: ["January", "February", "March", "April", "May", "June", "July"],
            datasets: [
                {
                    label: "Data Set One",
                    fill: true,
                    lineTension: 0.3,
                    backgroundColor: gradient1,
                    borderColor: gradient1,
                    borderCapStyle: "butt",
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: "miter",
                    borderWidth: 1,
                    pointBorderColor: gradient1,
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: gradient1,
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                    pointHoverBorderWidth: 2,
                    pointRadius: 1,
                    pointHitRadius: 10,
                    data: graph_data,
                    spanGaps: false,
                },
                {
                    label: "Data Set Two",
                    fill: true,
                    lineTension: 0.3,
                    backgroundColor: gradient2,
                    borderColor: gradient2,
                    borderCapStyle: "butt",
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: "miter",
                    borderWidth: 1,
                    pointBorderColor: gradient2,
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: gradient2,
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                    pointHoverBorderWidth: 2,
                    pointRadius: 1,
                    pointHitRadius: 10,
                    data: [50, 40, 50, 40, 45, 40, 30],
                    spanGaps: false,
                },
            ],
        },
    });
});
