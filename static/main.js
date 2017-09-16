// Process query params to populate forms
function getParameterByName(name, fallback) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? fallback : decodeURIComponent(results[1].replace(/\+/g, " "));
}

// Always send the CSRF token on AJAX requests
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


// Sorting
function replaceUrlParam(url, paramName, paramValue){
    if(paramValue == null)
        paramValue = '';
    var pattern = new RegExp('\\b('+paramName+'=).*?(&|$)')
    if(url.search(pattern)>=0){
        return url.replace(pattern,'$1' + paramValue + '$2');
    }
    return url + (url.indexOf('?')>0 ? '&' : '?') + paramName + '=' + paramValue
}

function updateSortFilters(caller) {
    var new_url = replaceUrlParam(window.location.href, 'sorting', $(caller).val());
    window.location.href = new_url;
}


// Global AJAX Operations
function toggleStar(caller, asin) {
    var starred = $(caller).hasClass('product-results-fave-starred');
    if (!starred) {
        $.post({
            url: "/favorites/",
            dataType:'json',
            data: {"asin": asin}
        });
    } else {
        $.ajax({
            method: "delete",
            url: "/favorites/?asin=" + asin
        });
    }
    $(caller).toggleClass('product-results-fave-starred');
}
function saveParams(name) {
    var paramString = $('form').serialize();
    $.post({
        url: "/saved-searches/",
        dataType:'json',
        data: {"paramString": paramString, "name": name}
    });
}
function deleteSavedSearch(id, name) {
    swal({
      title: "Are you sure?",
      text: "This will permanently delete the search '" + name + "'!",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Yes, delete it!",
      closeOnConfirm: false
    },
    function(){
        $.ajax({
            url: "/saved-searches/?id=" + id,
            type: "DELETE",
            success: function (result) { location.reload(); }
        });
    });
}


function updateProfitEstimations(element, unit_revenue, asin) {
    var target = $(element.parentElement).next().find('h2');
    var unit_cost = $(element).val();
    target.html("$" + (unit_revenue - unit_cost).toFixed(2));
    $.post({
        url: "/favorites/",
        data: {'asin': asin, 'unit_cost': unit_cost},
    });
}


// General UI functionality
$(document).ready((e) => {
  $("#limit").val(getParameterByName("limit", 50));
  $('#range-limit-value').text($('#limit').val());

  $("#min_volume").val(getParameterByName("min_volume", 50));
  $('#range-volume-value').text($('#min_volume').val());

  $("#min_price").val(getParameterByName("min_price", ''));
  $("#max_price").val(getParameterByName("max_price", ''));
  $("#min_reviews").val(getParameterByName("min_reviews", ''));
  $("#max_reviews").val(getParameterByName("max_reviews", ''));
  $("#query").val(getParameterByName("query", ""));

  // The default for sorting depends on page
  var sorting_default = null;
  if (location.href.lastIndexOf('/search/') != -1) {
    sorting_default = "-revenue";
  } else if (location.href.lastIndexOf('/searches/') != -1) {
    sorting_default = "-avg_revenue"
  } else if (location.href.lastIndexOf('/favorites/') != -1) {
    sorting_default = "-revenue"
  }
  $("#sorting").val(getParameterByName("sorting", sorting_default));


  $('#slide-out-nav').hide()
  $('.search-wrapper').hide()
//  $('.save-search-modal-wrapper').hide()
  $('.sort-wrapper').hide()

  //Side Menu

  $('#nav-button').on('click', () => {
    $('#slide-out-nav').show()
    $('body').css('overflow-y', 'hidden')
  });

  $('#slide-out-nav').on('click', () => {
    $('#slide-out-nav').hide()
    $('body').css('overflow-y', 'auto')
  });

  $('.slide-out-buttons').click((event) => {
    event.stopPropagation();
  });

  //Desktop Search
  $('#dt-search-button').click(() => {
    console.log($('#dt_limit').val());
  })

  //Search Screen
  $('#search-button').click(() => {
    $('.search-wrapper').show()
    $('section').css('overflow-y', 'hidden');
  });

  $('#save-search-button').click(() => {
    swal({
      title: "Save your Search!",
      text: "Specify a name for your search:",
      type: "input",
      showCancelButton: true,
      closeOnConfirm: true,
      animation: "slide-from-top",
      inputPlaceholder: "Name"
    },
    function(name){
      if (name === false) return false;
      if (name === "") {
        swal.showInputError("You need to specify a name.");
        return false
      }
      saveParams(name);
    });
  });

  $('#edit-search').click((e) => {
    $('.search-wrapper').show()

    $('#range-limit-value').html($(e.target).parent().parent().parent().prev().find($('.limit')).text())
    $('#limit').val($(e.target).parent().parent().parent().prev().find($('.limit')).text())

    $('#range-volume-value').html($(e.target).parent().parent().parent().prev().find($('.mnvol')).text())
    $('#min_volume').val($(e.target).parent().parent().parent().prev().find($('.mnvol')).text())

    $('#min_price').val($(e.target).parent().parent().parent().prev().find($('.mnprc')).text())

    $('#max_price').val($(e.target).parent().parent().parent().prev().find($('.mxprc')).text())

    $('#min_reviews').val($(e.target).parent().parent().parent().prev().find($('.mnrvw')).text())

    $('#max_reviews').val($(e.target).parent().parent().parent().prev().find($('.mxrvw')).text())

    // $('#sort-by').val($(e.target).parent().parent().parent().prev().find($('.sort-by')).text())

    $('#keywords').val($(e.target).parent().parent().parent().prev().find($('.kywrd')).text())

    console.log($(e.target).parent().parent().parent().prev().find($('.limit')).text())
  });

//  $('.save-search button').click(() => {
//    $('.save-search-modal-wrapper').show()
//    $('html, body').animate({
//      scrollTop: $('.save-search-modal-wrapper').offset().top
//    })
//    $('body').css('overflow', 'hidden')
//  });

  $('#cancel-save').click(() => {
    $('body').css('overflow-y', 'auto')
//    $('.save-search-modal-wrapper').hide()
  });

  $('#search-close').click(() => {
    $('.search-wrapper').hide()
    $('body').css('overflow-y', 'auto')
  });

  $('#limit').change(() => {
    $('#range-limit-value').text($('#limit').val())
  });

  $('#min_volume').change(() => {
    $('#range-volume-value').text($('#min_volume').val())
  });

  //Sort Screen

  $('#sort-show').click(() => {
    $('.sort-wrapper').show()
    $('body').css('overflow-y', 'hidden')
  });

  $('#sort-cancel').click(() => {
    $('.sort-wrapper').hide()
    $('body').css('overflow-y', 'auto')
  });

  $('#sort-done').click(() => {
    $('.sort-wrapper').hide()
    $('body').css('overflow-y', 'auto')
  });
})
