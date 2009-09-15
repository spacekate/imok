/** global variables **/
var signupForm;
var firstcontact = true;


/* on page load */
dojo.addOnLoad(function() {
    signupForm = dojo.byId("signupForm");
});

function addContact() {
    var contacts = dojo.byId('contacts');
    var contactlist = signupForm.contactlist;
    var contactErrorMsg = dojo.byId('contactErrorMsg');
    var email = signupForm.contactemail;

    if (email.value == '') {
        contactErrorMsg.innerHTML = 'Please enter an email address';
    }
    else if (!validateEmail(email)) {
        contactErrorMsg.innerHTML = '"' + email.value + '" is not a valid email address';
    }
    else {
        contactErrorMsg.innerHTML = '';

        if (firstcontact) {
            contacts.innerHTML = '';
            contactlist.value = '';
            firstcontact = false;
        } else {
            contacts.innerHTML += '<br />';
            contactlist.value += ',';
        }

        contacts.innerHTML += email.value;
        contactlist.value += email.value;

        // clear contact field and set focus ready for next email
        email.value = '';
    }

    email.focus();
}

function addContactOnReturn(event) {
    if (event.keyCode == dojo.keys.ENTER) {
        dojo.stopEvent(event); // stop form from being submitted
        signupForm.addcontact.click();
    }
}
