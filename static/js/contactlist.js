/* on page load */
dojo.addOnLoad(function() {
    getContactList();
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
}

function updateContactList(contactJSON) {
    var contacts = '';

    for (var i = 0; i < contactJSON.length; i++) {
        contacts += '<li>' + contactJSON[i].email +
                    ' <img src="" class="delete link" alt="x" title="click to delete this contact" ' +
                    'onclick="javascript:deleteContact(\'' + contactJSON[i].key + '\')" /></li>';
    }

    dojo.byId('contacts').innerHTML = contacts;
}
