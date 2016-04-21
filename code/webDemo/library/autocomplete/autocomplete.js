jQuery(function() {
    $('input#suggestBox').jsonSuggest({
        data: dataIpAnycast.listIpAnycast,
        minCharacters: 2,
        onSelect: callback
    });
});

function callback(item) {
    document.getElementById('loadLocation').click();
}
