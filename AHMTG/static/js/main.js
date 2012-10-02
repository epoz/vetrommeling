
  $('#makeseriesdoen').click(function(event) {
    var loc, v, _i, _len, _ref;
    event.preventDefault();
    loc = 'naam=' + encodeURI($('#serienaam').val());
    loc += '&adlibsearch=' + encodeURI($('#serieadlibsearch').val());
    _ref = $('.vraag:checked');
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      v = _ref[_i];
      loc += '&vraag=' + $(v).attr('rel');
    }
    return $.post('/makeseries/', loc, function(data) {
      return alert(data);
    });
  });

  $('#volgende').click(function(event) {
    var antw;
    event.preventDefault();
    antw = $('input[name="optie"]:checked').val();
    if (!antw) antw = $('#antwoord').val();
    if (!antw) {
      document.location = '.';
      return;
    }
    return $.post('/answer/', {
      'serievraag_pk': SERIEVRAAG_PK,
      'obj_id': OBJ_ID,
      'data': antw
    }, function() {
      return document.location = '.';
    });
  });
