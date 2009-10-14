/* global variables */
var form;
var monitored = true;
var commentInstructions = "Add any additional instructions here...";

dojo.addOnLoad(function () {
    form = dojo.byId('settingsForm');
    setupAlert();
});

function setupAlert() {
    var fields = findFields(form);

    for (var i = 0; i < fields.length; i++) {

        // set events for timeout field
        if (fields[i].name == "timeout") {
            refreshTimeout(fields[i]);

            dojo.connect(fields[i], "onchange", function() {
                refreshTimeout(this);
                if (monitored) {
                    refreshAlert(this);
                }
                highlightSaveSettings(true);
            });
        }
        else // set events for all other fields
        {
            dojo.connect(fields[i], "onkeyup", function() {
                refreshAlert(this);
                highlightSaveSettings(true);
            });
            dojo.connect(fields[i], "onchange", function() {
                refreshAlert(this);
                highlightSaveSettings(true);
            });
        }

        // set additional events for phone number fields
        if (fields[i].name == "phone" || fields[i].name == "mobile") {
            refreshPhone(fields[i]);

            dojo.connect(fields[i], "onkeyup", function() {
                refreshPhone(this);
            });
        }

        // add additional events for comment textbox
        if (fields[i].name == "comment") {
            addInstructions(fields[i], commentInstructions);
            refreshComment(fields[i]);

            dojo.connect(fields[i], "onkeyup", function() {
                refreshComment(this);
            });

            dojo.connect(fields[i], "onfocus", function() {
                refreshComment(this);
            });

            dojo.connect(fields[i], "onblur", function() {
                refreshComment(this);
            });
        }

        refreshAlert(fields[i]);
    }
}

function highlightSaveSettings(highlight) {
    dojo.forEach(dojo.query('[name=saveSettings]'), function(saveSettings) {
        //var instructions = dojo.query('.instructions')[0];
        if (highlight) {
            dojo.addClass(saveSettings, 'problem');
        } else {
            dojo.removeClass(saveSettings, 'problem');
        }

        dojo.forEach(dojo.query('.instructions', saveSettings), function(instructions) {
            if (highlight) {
                dojo.removeClass(instructions, 'hidden');
            } else {
                dojo.addClass(instructions, 'hidden');
            }
        });
    });


}

function refreshTimeout(field) {
    if (field.value == "-1") {
        setMonitoredStatus(false);
        return;
    } else if (!monitored) {
        setMonitoredStatus(true);
    }
}
function refreshPhone(field) {
    if (field.value == "") {
        dojo.addClass(dojo.byId(field.name + 'Sample'), 'hidden');
    } else {
        dojo.removeClass(dojo.byId(field.name + 'Sample'), 'hidden');
        dojo.removeClass(dojo.byId('phoneNumbers'), 'hidden');
    }
}
function refreshComment(field) {
    if (field.value == commentInstructions) {
        dojo.addClass(dojo.byId('commentIntro'), 'hidden');
    } else {
        dojo.removeClass(dojo.byId('commentIntro'), 'hidden');
    }
}

function refreshAlert(field) {
    dojo.query("[name^=" + field.name + "Sample]").forEach(function(sampleText) {
        var newValue = field.value;

        if (field.name == "timeout") {
            var tmpValue = newValue / 60;
            if (tmpValue < 1) {
                tmpValue=tmpValue.toFixed(2);
            }
            newValue = tmpValue + " hours";
 
        }

        if (field.name == "phone"  || field.name == "mobile") {
            var phone = dojo.byId('phone');
            var mobile = dojo.byId('mobile');

            if (phone.value == "" && mobile.value == "") {
                dojo.addClass(dojo.byId('phoneNumbers'), 'hidden');
            }

        }

        sampleText.innerHTML = newValue;
    });
}

function setMonitoredStatus(isMonitored) {
    monitored = isMonitored;

    if (isMonitored) {
        dojo.removeClass(dojo.byId("monitored"), "hidden");
        dojo.addClass(dojo.byId("unmonitored"), "hidden");
    } else {
        dojo.addClass(dojo.byId("monitored"), "hidden");
        dojo.removeClass(dojo.byId("unmonitored"), "hidden");
    }
}