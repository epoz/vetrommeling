$('#makeseriesdoen').click (event) ->
    event.preventDefault()
    loc = 'naam='+encodeURI($('#serienaam').val())
    loc += '&adlibsearch='+encodeURI($('#serieadlibsearch').val())
    for v in $('.vraag:checked')
        loc += '&vraag=' + $(v).attr('rel')
    $.post('/makeseries/', loc, (data) -> alert(data))

$('#makeseriespybossa').click (event) ->
    event.preventDefault()
    loc = 'naam='+encodeURI($('#serienaam').val())
    loc += '&adlibsearch='+encodeURI($('#serieadlibsearch').val())
    for v in $('.vraag:checked')
        loc += '&vraag=' + $(v).attr('rel')
    $.post('/makepybossa/', loc, (data) -> alert(data))

$('#volgende').click (event) -> 
    event.preventDefault()
    antw = $('input[name="optie"]:checked').val()
    if !antw 
        antw = $('#antwoord').val()
    if !antw
        document.location = '.'
        return
    $.post( '/answer/', {
        'serievraag_pk' : SERIEVRAAG_PK,
        'obj_id' : OBJ_ID,
        'data' : antw
        }, -> document.location = '.'
    )