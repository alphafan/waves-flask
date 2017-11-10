$('button[name="next_tab"]').click(function(e){
    e.preventDefault();
    var current_tab_index = $('ul#page_tab li').index( $('li.active') );
    $('ul#page_tab li:eq(' + (current_tab_index + 1) + ') a').tab('show')
});
$('button[name="prev_tab"]').click(function(e){
    e.preventDefault();
    var current_tab_index = $('ul#page_tab li').index( $('li.active') );
    $('ul#page_tab li:eq(' + (current_tab_index - 1) + ') a').tab('show')
});