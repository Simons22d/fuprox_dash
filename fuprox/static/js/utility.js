
    function getFrequency(item){
    thisVal =  item.value;
    if(thisVal === "null"){
        $("#type").prop("disabled",true);
        $("#statusOne").prop("selected",true);
    }else if(thisVal === 'day'){
        $("#type").removeAttr("disabled");
        $("#dateCont").show();
        $("#monthCont").hide();
        $("#weekCont").hide();
    }else if(thisVal === "week"){
        $("#type").removeAttr("disabled");
        $("#dateCont").hide();
        $("#monthCont").show();
        $("#weekCont").show();

    }else if(thisVal === 'month'){
        $("#type").removeAttr("disabled");
        $("#dateCont").hide();
        $("#monthCont").show();
        $("#weekCont").hide();
    }
}

const daysInMonth  = (month, year) => {
    return new Date(year, month, 0).getDate();
}

const updateWeek = (item) => {
    let month = $("#month").val()
    if(month !== ""){
        let daysInMonths = new Date(month);
        let yearDate = daysInMonths.getFullYear();
        let monthDate = daysInMonths.getMonth()+1;
        var days = daysInMonth(monthDate,yearDate);
        let weeks = Math.floor(days/7);
        let extraDays = days%7;
        if(extraDays > 0){
            // five weeks
            $("#five").show();
        }else{
            // four weeks
            $("#five").hide();
        }
    }else{
        let error = $("#error");
        let monthHandle = $("#month");
        error.html("Month Required. Please Select Select A Month")
        error.show();
        monthHandle.addClass("is-invalid")
        setTimeout(()=>{
            error.hide()
            monthHandle.removeClass("is-invalid")
        },5000);
    }
}


var start = new Date(),
            prevDay,
            startHours = 8;
// 09:00 AM
start.setHours(8);
start.setMinutes(0);
// If today is Saturday or Sunday set 10:00 AM
if ([6, 0].indexOf(start.getDay()) !== -1) {
    start.setHours(10);
    startHours = 10
}
// var minHours =;
// var minDate = ;
// minDate : today;
$('#dailyCal').datepicker({
    language: 'en',
    startDate: start,
    maxDate: start,
    autoClose: true,
    position: "top left",
    onSelect: function (fd, d, picker) {
        // Do nothing if selection was cleared
        if (!d) return;
        let day = d.getDay();
        // Trigger only if date is changed
        if (prevDay !== undefined && prevDay === day) return;
        prevDay = day;
        // If chosen day is Saturday or Sunday when set
        // hour value for weekends, else restore defaults
        if (day === 6 || day === 0) {
            picker.update({
                minHours: 10,
                maxHours: 16
            })
        } else {
            picker.update({
                minHours: 9,
                maxHours: 18
            })
        }
    }
});


$('#month').datepicker({
language: 'en',
startDate: start,
autoClose : true,
view : "months",
minView : "months",
maxDate : start,
dataMinView : "months",
dataView : "months",
position: "top left",
onSelect: function (fd, d, picker) {
    // Do nothing if selection was cleared
    if (!d) return;
    var day = d.getDay();
    // Trigger only if date is changed
    if (prevDay !== undefined && prevDay === day) return;
    prevDay = day;
    // If chosen day is Saturday or Sunday when set
    // hour value for weekends, else restore defaults
    if (day === 6 || day === 0) {
        picker.update({
            minHours: 10,
            maxHours: 16
        })
    } else {
        picker.update({
            minHours: 9,
            maxHours: 18
        })
    }
}
});