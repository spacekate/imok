/* on page load */
dojo.addOnLoad(function() {
    getContactList();

    addInstructions(dojo.byId('newContact'), "Enter email address");
});

function getContactList() {
    dojo.xhrGet({
	    url: "/contact/list/",
        handleAs: "json",
        load: function(response, ioArgs) {
            //evaluate JSON reponse
            response = eval(response);

            updateContactList(response);
        },
        error : function(response, ioArgs) {
            //do nothing
        }
	});
}

function addContact(addContactForm) {
    var email = addContactForm.newContact;

    dojo.xhrGet({
	    url: "/contact/add/",
	    form: addContactForm,
        handleAs: "json",
        load: function(response, ioArgs) {
            //evaluate JSON reponse
            response = eval(response);

            updateContactList(response);
        },
        error : function(response, ioArgs) {
            //do nothing
        }
	});

    // hide detailNote
    dojo.addClass(dojo.byId('newContactDetail'), 'hidden');

    // clear contact field and set focus ready for next email
    email.value = '';
    email.focus();
    setDetailNotePosition(email);
}

function deleteContact(contactId) {
    dojo.xhrGet({
	    url: "/contact/delete/?contactId=" + contactId,
        handleAs: "json",
        load: function(response, ioArgs) {
            //evaluate JSON reponse
            response = eval(response);

            updateContactList(response);
        },
        error : function(response, ioArgs) {
            //do nothing
        }
	});

    // hide detailNote
    dojo.addClass(dojo.byId('deleteDetail'), 'hidden');
}

function updateContactList(contactJSON) {
    var contactlist = dojo.byId('contacts');

    contactlist.innerHTML = '';

    for (var i = 0; i < contactJSON.contacts.length; i++) {
        var email = contactJSON.contacts[i].email;
        var status = contactJSON.contacts[i].status;
        var key = contactJSON.contacts[i].key;
        displayContact(email, status, key);
    }

/*
    // test to show active and declined contacts
    displayContact('diver.dan@surethingmate.to', 'active', '556677');
    displayContact('bob.jelly@nogo.to', 'declined', '889900');
*/

    dojo.byId('contactsMsg').innerHTML = contactJSON.message;

    // show/hide statusKey and addContactsReminder
    if (contactJSON.contacts.length > 0) {
        dojo.removeClass(dojo.byId('statusKey'), 'hidden');

        var noContacts = dojo.byId('noContacts');
        if (noContacts && !dojo.hasClass(noContacts, 'hidden')) {
            dojo.addClass(noContacts, 'hidden');
        }
    } else {
        dojo.addClass(dojo.byId('statusKey'), 'hidden');

        var noContacts = dojo.byId('noContacts');
        if (noContacts && dojo.hasClass(noContacts, 'hidden')) {
            dojo.removeClass(noContacts, 'hidden');
        }
    }
}

function displayContact(email, status, key) {
    var contactlist = dojo.byId('contacts');
    var newRow = document.createElement('tr');
    var emailCell = document.createElement('td');
    var deleteCell = document.createElement('td');
    var statusSpan = document.createElement('span');

    dojo.addClass(newRow, 'highlightable ' + status);

    emailCell.name = key;
    emailCell.innerHTML = email + "<br />";

    deleteCell.innerHTML = 'x';
    dojo.addClass(deleteCell, 'delete');
    dojo.attr(deleteCell, 'id', key);
    dojo.connect(deleteCell, "onclick", function() {
        deleteContact(this.id);
    });
    dojo.connect(deleteCell, "onmouseover", function() {
        dojo.addClass(this.parentNode, "problem");
        toggleDetailNote(this, true, "deleteDetail");
    });
    dojo.connect(deleteCell, "onmouseout", function() {
        dojo.removeClass(this.parentNode, "problem");
        toggleDetailNote(this, false, "deleteDetail");
    });

    statusSpan.name = status;
    dojo.addClass(statusSpan, 'status');
    statusSpan.innerHTML = status;

    dojo.place(newRow, contactlist, 'last');
    dojo.place(emailCell, newRow, 'last');
    dojo.place(deleteCell, newRow, 'first');
    dojo.place(statusSpan, emailCell, 'last');
}
