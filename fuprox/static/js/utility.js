var ctx = document.getElementById('doughnut').getContext('2d');
var doughnut = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ["New","Assigned","Resolved","Closed"],
        datasets: [
            {
                label: "Population (millions)",
                backgroundColor: ["Red","Orange","Yellow","Green"],
                data: [0,0,2,0]
            }
        ]
    },
    options: {
        title: {
            display: true,
            text: 'Summary Of Done And Pending Tasks'
        }
    }
});


var ctx = document.getElementById('myChart').getContext('2d');
var make = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ["New","Assigned","Resolved","Closed"],
        datasets: [
            {
                label: "Population (millions)",
                backgroundColor: ["Red","Orange","Yellow","Green"],
                data: [0,0,2,0]
            }
        ]
    },
    options: {
        title: {
            display: true,
            text: 'Summary Of Done And Pending Tasks'
        }
    }
});