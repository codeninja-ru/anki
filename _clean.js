/**
 * finds divs by .clean classn and cleans their html and fixes the bold's divs
 * for example: 
 * <div>bla <span style="font-wight: 600">ha</span></div> is be converted into bal <b>ha</b>
 *
 * @author vmayorov
 */
class BNode {
    constructor(html) {
        this.html = html;
    }
    toString() {
        return '<b>' + this.html + '</b>';
    }
}

function isBold(node) {
    return node.style['font-weight'] >= 600;
}

function parseNode(node) {
    var nodes = [...node.childNodes].map((child) => {
        if (child instanceof Text) {
            return child.textContent;
        } else if (child instanceof HTMLElement) {
            var html = parseNode(child);
            return isBold(child) ? new BNode(html) : html;
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

function cleanHtml() {
    document.querySelectorAll('.clean').forEach(function(elm) {
        var newHtml = parseNode(elm).trim();
        elm.innerHTML = newHtml;
    });
}
