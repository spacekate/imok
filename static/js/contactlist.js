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

    // clear contact field and set focus ready for next email
    email.value = '';
    email.focus();
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

    // put focus in email input box
    dojo.byId('newContact').focus();
}

function updateContactList(contactJSON) {
    var contactlist = dojo.byId('contacts');

    contactlist.innerHTML = '';

    for (var i = 0; i < contactJSON.contacts.length; i++) {
        var newRow = document.createElement('tr');
        var emailCell = document.createElement('td');
        var deleteCell = document.createElement('td');

        dojo.addClass(newRow, 'highlightable');

        emailCell.innerHTML = contactJSON.contacts[i].email;

        deleteCell.innerHTML = 'x';
        dojo.addClass(deleteCell, 'delete');
        dojo.attr(deleteCell, 'title', 'click to delete this contact');
        dojo.attr(deleteCell, 'id', contactJSON.contacts[i].key);
        dojo.connect(deleteCell, "onclick", function() {
            deleteContact(this.id);
        });
        dojo.connect(deleteCell, "onmouseover", function() {
            dojo.addClass(this.parentNode, "problem");
        });
        dojo.connect(deleteCell, "onmouseout", function() {
            dojo.removeClass(this.parentNode, "problem");
        });

        dojo.place(newRow, contactlist, 'last');
        dojo.place(emailCell, newRow, 'last');
        dojo.place(deleteCell, newRow, 'first');
    }

    dojo.byId('contactsMsg').innerHTML = contactJSON.message;
}
