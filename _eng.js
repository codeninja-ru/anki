var refresh = (function(document) {
    /**
     * call the function fn when DOM is ready
     */
    function domReady(fn) {
        // If we're early to the party
        document.addEventListener("DOMContentLoaded", fn);
        // If late; I mean on time.
        if (document.readyState == "interactive" || document.readyState == "complete" ) {
            fn();
        }
    }

    /**
     * parse custom cloze
     */
    function parseBCloze() {
        document.querySelectorAll('.cloze').forEach(function (elm) {
            var brex = new RegExp('<b>([^<]+)</b>', 'ig');
            var html = elm.innerHTML;
            elm.dataset.back = html;
            if (html.match(brex)) {
                elm.innerHTML = html.replace(brex, '<span class="current-cloze" data-text="$1">[...]</span><span class="cloze-answer">$1</span>');
            } 
            elm.classList.remove('cloze');
        });
    }

    class BNode {
        constructor(html) {
            this.html = html;
        }
        toString() {
            return '<b>' + this.html + '</b>';
        }
    }

    class INode {
        constructor(html) {
            this.html = html;
        }
        toString() {
            return '<i>' + this.html + '</i>';
        }
    }

    class BrNode {
        toString() {
            return '<br/>';
        }
    }

    function isBold(node) {
        return node.style['font-weight'] >= 600 || node.style['font-weight'] == 'bold' || node.tagName == 'B';
    }

    function isItalic(node) {
        return node.style['font-style'] == 'italic' || node.tagName == 'I';
    }

    function isBrNode(node) {
        return node.tagName == 'BR';
    }

    function parseNode(node) {
        var nodes = [...node.childNodes].map((child) => {
            if (child instanceof Text) {
                return child.textContent;
            } else if (child instanceof HTMLElement) {
                var html = parseNode(child);
                if (isBold(child)) {
                    return new BNode(html);
                } else if (isItalic(child)) {
                    return new INode(html);
                } else if (isBrNode(child)) {
                    return new BrNode(child);
                }

                return html;
            } else {
                throw new Error('unknow type');
            }
        });

        var result = [];
        var prevNode = null;
        for (var node of nodes) {
            if (node instanceof BNode) {
                if (prevNode != null) {
                    result.pop();
                    result.push(new BNode(prevNode.html + node.html));
                } else {
                    result.push(node);
                }
                prevNode = node;
            } else {
                result.push(node);
                prevNode = null;
            }
        }

        return result.join('');
    }

    /**
     * finds divs by .clean classn and cleans their html and fixes the bold's divs
     * for example: 
     * <div>bla <span style="font-wight: 600">ha</span></div> is be converted into bal <b>ha</b>
     *
     * @author vmayorov
     */
    function cleanHtml() {
        document.querySelectorAll('.clean').forEach(function(elm) {
            var newHtml = parseNode(elm).trim();
            elm.innerHTML = newHtml;
            elm.classList.remove('clean');
        });
    }

    domReady(() => {
        cleanHtml();
        parseBCloze();
    });

    return () => {
        domReady(() => {
            cleanHtml();
            parseBCloze();
        });
    };

})(document);
