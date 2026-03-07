function splitLines(s) {
    const out = [];

    let startPos = 0;
    while (startPos < s.length) {
        let posCR = s.indexOf('\r', startPos);
        let posLF = s.indexOf('\n', startPos);

        const hasCR = (posCR >= 0);
        const hasLF = (posLF >= 0);
        const hasCRLF = (hasCR && posLF === posCR + 1);

        if (!hasCR && !hasLF) {
            // neither line terminator => last line
            if (startPos > 0) {
                out.push(s.substring(startPos));
            }
            break;
        }


        let splitOnCR = hasCR;
        if (hasLF && posLF < hasCR) {
            splitOnCR = false;
        }

        const splitPos = splitOnCR ? posCR : posLF;
        out.push(s.substring(startPos, splitPos));
        startPos = splitPos + 1;

        if (hasCRLF) {
            // skip LF after CR
            startPos++;
        }
    }

    return out;
}

function wrapPreformattedLines() {
    for (const elemPre of document.getElementsByTagName('pre')) {
        // process only if text node underneath <pre>
        const children = elemPre.childNodes;
        if (children.length != 1 || !(children[0] instanceof Text || (children[0] instanceof HTMLElement && children[0].tagName == 'CODE'))) {
            console.log('wrong type for wrap', children);
            continue;
        }

        let out = '';

        const lines = splitLines(children[0].textContent);
        for (const line of lines) {
            out += '<code class="line">' + line + '</code>\n';
            // .replace(reLineBreak, '')
        }

        elemPre.innerHTML = out;
    }
}

function initBoxes() {
    const cssClassCollapsed = 'box-collapsed';
    const cssClassExpanded = 'box-expanded';

    for (const elemBox of document.querySelectorAll('div.box')) {
        const elemHeader = elemBox.querySelector('.box-header');

        // boxes without header are "decorative" without function, skip
        if (!elemHeader) {
            continue;
        }

        if (elemBox.classList.contains('default-collapsed')) {
            elemBox.classList.add(cssClassCollapsed);
        } else {
            elemBox.classList.add(cssClassExpanded);
        }

        elemHeader.addEventListener('click', function () {
            const wasCollapsed = elemBox.classList.contains(cssClassCollapsed);
            if (wasCollapsed) {
                // expand
                elemBox.classList.add(cssClassExpanded);
                elemBox.classList.remove(cssClassCollapsed);
            } else {
                // collapse
                elemBox.classList.add(cssClassCollapsed);
                elemBox.classList.remove(cssClassExpanded);
            }
        });
    }
}


function initNavigation() {
    const menuItemsByRefId = {};
    for (const elemMenuAnchor of document.querySelectorAll('aside > ul li a')) {
        const href = elemMenuAnchor.attributes.getNamedItem('href').value;
        if (!href.startsWith('#')) {
            continue;
        }

        const ref = href.substring(1);
        menuItemsByRefId[ref] = elemMenuAnchor;
    }

    const elemsReferenced = [];
    for (const elemContentId of document.querySelectorAll('main #inner [id]')) {
        const contentId = elemContentId.id;
        if (!(contentId in menuItemsByRefId)) {
            continue;
        }

        elemsReferenced.push(elemContentId);
    }

    function markActiveItem() {
        // content positions are offset by header height
        const headerHeight = document.querySelector('header').offsetHeight;

        let closestNegativeOrZero = null;
        let closestPositive = null;
        for (const elemReferenced of elemsReferenced) {
            // NOTE: content scrolls out of the "client rect" (window-relative?) bbox to negative positions
            const elemPos = elemReferenced.getBoundingClientRect().y - headerHeight;
            if (elemPos <= 0) {
                if (!closestNegativeOrZero || elemPos > closestNegativeOrZero[1]) {
                    closestNegativeOrZero = [elemReferenced, elemPos];
                }
            } else {
                if (!closestPositive || elemPos < closestPositive[1]) {
                    closestPositive = [elemReferenced, elemPos];
                }
            }
        }

        const closest = closestNegativeOrZero || closestPositive;
        if (!closest) {
            return;
        }

        const contentId = closest[0].id;
        const elemMenuNewActive = menuItemsByRefId[contentId];
        if (!elemMenuNewActive) {
            return;
        }

        const elemPreviousActive = document.querySelector('aside > ul li a.active');
        if (elemPreviousActive) {
            if (elemPreviousActive === elemMenuNewActive) {
                // nothing to change, still active
                return;
            }

            // unmark previous menu item
            elemPreviousActive.classList.remove('active');
        }

        // mark new menu item
        elemMenuNewActive.classList.add('active');
    }

    window.addEventListener('scroll', function () {
        markActiveItem();
    });
    markActiveItem();

    // add click listener to scroll to sections with required header offset
    for (const elemReferenced of elemsReferenced) {
        const elemMenuAnchor = menuItemsByRefId[elemReferenced.id];
        elemMenuAnchor.addEventListener('click', function (e) {
            const headerHeight = document.querySelector('header').offsetHeight;

            window.scrollBy({
                top: elemReferenced.getBoundingClientRect().y - headerHeight + 1, // offset by 1 to compensate for sporadic misdetection in menu active mark
                behavior: 'smooth',
            })

            e.preventDefault();
            return false;
        });
    }

    // FIXME: scroll to URL reference on load
}

function init() {
    wrapPreformattedLines();

    initBoxes();
    initNavigation();
}

document.onreadystatechange = function (e) {
    if (document.readyState === 'complete') {
        init();
    }
}