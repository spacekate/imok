/** global variables **/
var firstcontact = true;

function addContact(form) {
    var contactlist = dojo.byId('contactlist');
    var email = form.contactemail.value;

    if (email == '') {
        dojo.byId('contactErrorMsg').innerHTML = 'Please enter an email address';
    }
    else {
        dojo.byId('contactErrorMsg').innerHTML = '';

        if (firstcontact) {
            contactlist.innerHTML = '';
            firstcontact = false;
        } else {
            contactlist.innerHTML += '<br />';
        }

        contactlist.innerHTML += email;

        // clear contact field
        form.contactemail.value = '';

        form.contactemail.focus();
    }
}