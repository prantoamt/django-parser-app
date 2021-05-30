var month = new Array();
month[0] = "January";
month[1] = "February";
month[2] = "March";
month[3] = "April";
month[4] = "May";
month[5] = "June";
month[6] = "July";
month[7] = "August";
month[8] = "September";
month[9] = "October";
month[10] = "November";
month[11] = "December";

getCurrentDateTime = () => {
	var currentdate = new Date(); 
  var formatter_datetime = (month[currentdate.getMonth()])  + " "
              +  currentdate.getDate() + ", " 
              + currentdate.getFullYear() + " @ "  
              + currentdate.getHours() + ":"  
              + currentdate.getMinutes() + ":" 
              + currentdate.getSeconds();
  let kwargs = {'formatter_datetime': formatter_datetime, 'currentdate': currentdate}
	return kwargs;			
}

setupLoader = () => {
  $(document).ajaxSend(function() {
    $("#overlay").fadeIn(300);　
    });
}

stopLoader = () => {
  setTimeout(function(){
    $("#overlay").fadeOut(100);
  },500);
}


createGETRequest = (url) => {
  $.ajax({
    url: url,
    type: 'GET',
    cache: false,
    async: false
  })
  .done(function (data) {
    stopLoader()
    console.log(data, 'in returned value')
    return data
  })
  .fail(function (res) {
      stopLoader()
      toastr['error'](res)
      return null
  })
}


createAsyncPOSTRequest = (endpoint, data) => {
  const csrftoken = getCookie('csrftoken');
  $.ajax({ 
    url: endpoint,
    data: data,
    type: 'POST',
    headers: {
        'X-CSRFToken': csrftoken
    },
    contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
    processData: false, // NEEDED, DON'T OMIT THIS
    async: false,
    success: function(res){
        stopLoader()
        console.log(res)
    },
    error: function(err){
        stopLoader()
        toastr["error"](err['responseJSON']['detail'])
        console.log(res)
    }
});
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}