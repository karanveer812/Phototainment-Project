"use strict";

console.log(pie_data)

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
    // Bar Chart
    // ------------------------------------------------------ //
    var BARCHARTEXMPLE = document.getElementById("barChartExample");
    var barChartExample = new Chart(BARCHARTEXMPLE, {
        type: "bar",
        options: {
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
            labels: bar_label,
            datasets: [
                {
                    label: "Data Set 1",
                    backgroundColor: [gradient1, gradient1, gradient1, gradient1, gradient1, gradient1, gradient1],
                    hoverBackgroundColor: [gradient1, gradient1, gradient1, gradient1, gradient1, gradient1, gradient1],
                    borderColor: [gradient1, gradient1, gradient1, gradient1, gradient1, gradient1, gradient1],
                    borderWidth: 1,
                    data: bar_data,
                }
            ],
        },
    });


    // ------------------------------------------------------- //
    // Doughnut Chart
    // ------------------------------------------------------ //
    var DOUGHNUTCHARTEXMPLE = document.getElementById("doughnutChartExample");
    var pieChartExample = new Chart(DOUGHNUTCHARTEXMPLE, {
        type: "doughnut",
        options: {
            cutoutPercentage: 70,
        },
        data: {
            labels: pie_label,
            datasets: [
                {
                    data: pie_data,
                    borderWidth: 0,
                    backgroundColor: ["#ff0000", "#49cd8b", "#54e69d", "#71e9ad"],
                    hoverBackgroundColor: ["#ff4400", "#49cd8b", "#54e69d", "#71e9ad"],
                },
            ],
        },
    });

    var pieChartExample = {
        responsive: true,
    };

});
