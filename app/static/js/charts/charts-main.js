"use strict";

console.log(pie_data)
bar_data.push(0)

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
    // Events Chart
    // ------------------------------------------------------ //
    var EVENTCHART = document.getElementById("EventChart");
    var successfulEvent = new Chart(EVENTCHART, {
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
            legend: {
                display: false,
            },
        },
        data: {
            labels: bar_label,
            datasets: [
                {
                    label: "Events",
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
    // Successful Events Chart
    // ------------------------------------------------------ //
    var SUCCESSFULEVENTS = document.getElementById("SuccessfulEvents");
    var pieChartExample = new Chart(SUCCESSFULEVENTS, {
        type: "doughnut",
        options: {
            cutoutPercentage: 70,
        },
        data: {
            labels: pie_label,
            datasets: [
                {
                    data: pie_data,
                    borderWidth: 3,
                    backgroundColor: ["#ff0000", "#49cd8b", "#54e69d", "#71e9ad"],
                    hoverBackgroundColor: ["#ff4400", "#49cd8b", "#54e69d", "#71e9ad"],
                },
            ],
        },
    });

    var pieChartExample = {
        responsive: true,
    };


// ------------------------------------------------------- //
    // Cost Chart
    // ------------------------------------------------------ //
    var COSTCHART = document.getElementById("CostChart");
    var pieChartExample = new Chart(COSTCHART, {
        type: "doughnut",
        options: {
            cutoutPercentage: 70,
        },
        data: {
            labels: pie_label,
            datasets: [
                {
                    data: [1, 2, 3],
                    borderWidth: 3,
                    backgroundColor: ["#ff0000", "#49cd8b", "#54e69d", "#71e9ad"],
                    hoverBackgroundColor: ["#ff4400", "#49cd8b", "#54e69d", "#71e9ad"],
                },
            ],
        },
    });

    var pieChartExample = {
        responsive: true,
    };



    // ------------------------------------------------------- //
    // Bar Chart 1
    // ------------------------------------------------------ //
    var BARCHART1 = document.getElementById("barChart1");
    var barChartHome = new Chart(BARCHART1, {
        type: "bar",
        options: {
            scales: {
                xAxes: [
                    {
                        display: true,
                    },
                ],
                yAxes: [
                    {
                        display: true,
                    },
                ],
            },
            legend: {
                display: false,
            },
        },
        data: {
            labels: graph_labels,
            datasets: [
                {
                    label: "Cost",
                    backgroundColor: [
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                    ],
                    borderColor: [
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                        "#44b2d7",
                    ],
                    borderWidth: 0,
                    data: graph_data2,
                },
            ],
        },
    });


    // ------------------------------------------------------- //
    // Pie Chart
    // ------------------------------------------------------ //
    var PIECHARTEXMPLE = document.getElementById("pieChartExample");
    var pieChartExample = new Chart(PIECHARTEXMPLE, {
        type: "pie",
        data: {
            labels: cost_chart_label,
            datasets: [
                {
                    data: cost_chart_data,
                    borderWidth: 0,
                    backgroundColor: ["#44b2d7", "#59c2e6", "#71d1f2", "#96e5ff"],
                    hoverBackgroundColor: ["#44b2d7", "#59c2e6", "#71d1f2", "#96e5ff"],
                },
            ],
        },
    });

    var pieChartExample = {
        responsive: true,
    };



});



