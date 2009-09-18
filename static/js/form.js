/*** Functionality to highlight rows onmouseover, validate fields and show errors ***/

// global variables
var numErrors = 0;
var haltHighlighting = false;

// detect highlightable rows on load
dojo.addOnLoad(function () {
    var showAdvanced = false;
    var highlightRows = dojo.query("[class^=highlightable]");

    for (var i = 0; i < highlightRows.length; i++) {
        // add onmouseover events
        dojo.connect(highlightRows[i], "onmouseover", function () {
            toggleHighlight(this, true);
            toggleDetailNote(findFields(this)[0], true);
        });
        dojo.connect(highlightRows[i], "onmouseout", function () {
            toggleHighlight(this, false);
            toggleDetailNote(findFields(this)[0], false);
        });

        // add field events
        var fields = findFields(highlightRows[i]);

        for (var j = 0; j < fields.length; j++) {
            dojo.connect(fields[j], "onfocus", function () {
                toggleDetailNote(this, true);
                toggleHighlight(this.parentNode.parentNode, true);
                haltHighlighting = true;
            });
            dojo.connect(fields[j], "onblur", function () {
                haltHighlighting = false;
                toggleHighlight(this.parentNode.parentNode, false);
                toggleDetailNote(this, false);

                if (dojo.hasClass(this, "validate") && this.value != '') {
                    validate(this);
                }
            });
            if (dojo.hasClass(fields[j], "validate")) {
                var eventType = "onkeyup";
                if (fields[j].tagName == "SELECT" || dojo.attr(fields[j], "type") == "file") {
                    eventType = "onchange"
                }
                dojo.connect(fields[j], eventType, function () {
                    var row = this.parentNode.parentNode;

                    if (dojo.hasClass(row, "problem")) {
                        validate(this);
                    }
                });
            }

            // show advanced options if any have a value
            if (dojo.hasClass(fields[j].parentNode.parentNode, "advanced") &&
                fields[j].value && !showAdvanced) {
                showAdvanced = true;
                toggleAdvancedOptions();
            }
        }
    }
});

function findFields(section) {
    if (!section) {
        return dojo.query("input").concat(dojo.query("select"));
    }

    return dojo.query("input", section).concat(dojo.query("select", section));
}

// highlight/unhighlight row and show/hide comments
function toggleHighlight(/*dom object*/row, /*boolean*/show) {
    if (haltHighlighting) return;

    var field = findFields(row)[0];

    if (show) {
        dojo.addClass(row, "highlight");

        if (field && !dojo.hasClass(row, "problem")) {
            showComment(field, "note");
        }
    } else {
        dojo.removeClass(row, "highlight");

        if (field && !dojo.hasClass(row, "problem")) {
            showComment(field, "placeholder");
        }
    }

    if (field) {
        // toggle highlight for any comment rows
        var comments = dojo.query("[name^=" + field.name + "Comment]");

        for (var i = 0; i < comments.length; i++) {
            var commentRow = comments[i].parentNode;
            if (commentRow != row) {
                toggleHighlight(commentRow, show);
            }
        }
    }
}

// shows/hides associated detail div
function toggleDetailNote(field, show) {
    var detailNote = dojo.byId(field.name + "Detail");

    if (haltHighlighting || !detailNote) return;
    
    if (show) {
        var coords = dojo.coords(field.parentNode);
        var leftPadding = 200;
        var heightPadding = -4;

        dojo.style(detailNote, {
            "top" : coords.y + "px",
            "left" : (coords.x + leftPadding) + "px"
        });

        dojo.removeClass(detailNote, "hidden");
    } else {
        dojo.addClass(detailNote, "hidden");
    }
}

function showComment(/*dom object*/field, /*string*/commentClass) {
    if (!commentClass) commentClass = "placeholder";
    var comments = dojo.query("[name^=" + field.name + "Comment]");

    for (var i = 0; i < comments.length; i++) {
        if (dojo.hasClass(comments[i], commentClass)) {
            dojo.removeClass(comments[i], "hidden");
        } else if (!dojo.hasClass(comments[i], "hidden")) {
            dojo.addClass(comments[i], "hidden");
        }
    }
}



// validation functions
function validateAll(form) {
    var valid = true;
    var fields = findFields(form);

    for (var i = fields.length-1; i >= 0; i--) { // iterate backwards so the topmost error gets focus
        if (dojo.hasClass(fields[i], "validate")) {
            valid = validate(fields[i]) && valid;
        }
    }

    return valid;
}

function validate(field) {
    var valid = true;
    var row = field.parentNode.parentNode;
    var commentCell = dojo.query("[name^=" + field.name + "Comment]")[0];

    // validate field
    if (dojo.hasClass(field, "email")){
        valid = validateEmail(field);
    }
    else if (dojo.hasClass(field, "url")) {
        valid = validateUrl(field);
    }
    else if (dojo.hasClass(field, "price")) {
        valid = validatePrice(field);
    }
    else {
        valid = validateNotEmpty(field);
    }

    // highlight invalid field
    if (!valid) {
        if (!dojo.hasClass(row, "problem")) {
            numErrors++;
            dojo.addClass(row, "problem");
            // highlight comment row
            if (commentCell) {
                dojo.addClass(commentCell.parentNode, "problem");
            }
            // show error message
            showComment(field, "error");
        }

        // give field focus unless it's a file upload field
        if (!dojo.hasClass(field, "file")) {
            field.focus();
        }
    } else if (valid && dojo.hasClass(row, "problem")) {
        numErrors--;
        dojo.removeClass(row, "problem");
        // highlight comment row
        if (commentCell) {
            dojo.removeClass(commentCell.parentNode, "problem");
        }
        // hide error message
        showComment(field, "note");
        toggleHighlight(row, false);
    }

    // show/hide submit button
    if (numErrors > 0) {
        toggleSubmit("cancel");
    }
    else {
        toggleSubmit("action");
    }

    return valid;
}

function validateEmail(field) {
    var regExp = /^([a-zA-Z0-9_.-])+@([a-zA-Z0-9_.-])+\.([a-zA-Z])+([a-zA-Z])+/;

    return regExp.test(field.value);
}

function validateUrl(field) {
    var regExp = new RegExp();
    regExp.compile("^[A-Za-z0-9-_/.]+$"); 

    return regExp.test(field.value);
}

function validatePrice(field) {
    return field.value.match(/^\d+\.+\d{2}$/);
}

function validateNotEmpty(field) {
    field.value.trim;
    return field.value != "";
}

// show submit if there are no errors, otherwise display error message instead
function toggleSubmit (/*boolean*/submitClass) {
    var submits = dojo.query("[name^=submit]");

    for (var i = 0; i < submits.length; i++) {
        if (dojo.hasClass(submits[i], submitClass)) {
            dojo.removeClass(submits[i], "hidden");
        } else if (!dojo.hasClass(submits[i], "hidden")) {
            dojo.addClass(submits[i], "hidden");
        }
    }
}

// submit form from an onclick event
function submitForm(form) {
    if (validateAll()) {
        form.submit();
    }
}

// show/hide advanced options
function toggleAdvancedOptions() {
    var toggleImg = dojo.byId("toggleAdvanced");

    dojo.query(".advanced").forEach(function (advanced) {
        if (dojo.hasClass(advanced, "toggle")) {
            return; // this is the toggle row, do not hide it
        }
        if (toggleImg.alt == "show") {
            dojo.removeClass(advanced, "hidden");
        } else {
            dojo.addClass(advanced, "hidden");
        }
    });

    if (toggleImg.alt == "show") {

            toggleImg.src = "/static/admin/images/contract.gif"
            toggleImg.alt = "hide";
    } else {
        
            toggleImg.src = "/static/admin/images/expand.gif"
            toggleImg.alt = "show";
    }
}

// toggle an element with an id of elementName
// if there is a corresponding element with an id elementName + "Toggle",
// it will be treated as a contract/expand image
// if tableRow is specified, it's border will be set to 'none' while element is shown
function toggleElement(elementName, tableRow) {
    var element = dojo.byId(elementName);
    var toggleImg = dojo.byId(elementName + "Toggle");

    if (dojo.hasClass(element, "hidden")) {
        dojo.removeClass(element, "hidden");
        toggleImg.src = "/static/admin/images/contract.gif"
        toggleImg.alt = "show";
        if (tableRow) {
            dojo.addClass(tableRow, "noborder");
        }
    } else {
        dojo.addClass(element, "hidden");
        toggleImg.src = "/static/admin/images/expand.gif"
        toggleImg.alt = "hide";
        if (tableRow) {
            dojo.removeClass(tableRow, "noborder");
        }
    }
}
