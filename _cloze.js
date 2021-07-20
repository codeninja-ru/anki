function parseCloze() {
    document.querySelectorAll('.cloze').forEach(function (elm) {
        var brex = new RegExp('<b>([^<]+)</b>', 'ig');
        var html = elm.innerHTML;
        elm.dataset.back = html;
        if (html.match(brex)) {
            elm.innerHTML = html.replace(brex, '<span class="current-cloze" data-text="$1">[...]</span>');
        } 
    });
}
