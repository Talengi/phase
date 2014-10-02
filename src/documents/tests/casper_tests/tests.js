var casper = casper || {};
var document_list_url = casper.cli.options['url'];

casper.options.clientScripts.push("../../../static/js/vendor/sinon.js");

function inject_cookies() {
    var m = casper.cli.options['url-base'].match(/https?:\/\/([^:]+)(:\d+)?\//);
    var domain = m ? m[1] : 'localhost';

    for (var key in casper.cli.options) {
        if (key.indexOf('cookie-') === 0) {
            var cn = key.substring('cookie-'.length);
            var c = phantom.addCookie({
                name: cn,
                value: casper.cli.options[key],
                domain: domain
            });
        }
    }
}
inject_cookies();

casper.test.begin('Documents are fetched on page load', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertTitle('Phase');
        casper.wait(500);
        test.assertSelectorHasText('#display-results', '1 document on 1')
        test.assertElementCount('table#documents tbody tr', 1);
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Clicking on a checkbox add a class to the tr', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertDoesntExist('tr.selected');
    });

    casper.then(function() {
        casper.click('td.columnselect input[type=checkbox]');
        test.assertExists('tr.selected');
    });

    casper.then(function() {
        casper.click('td.columnselect input[type=checkbox]');
        test.assertDoesntExist('tr.selected');
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Buttons are enabled on checkbox click', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertExists('button#download-button.disabled');
    });

    casper.then(function() {
        casper.click('td.columnselect input[type=checkbox]');
        test.assertDoesntExist('button#download-button.disabled');
        test.assertExists('button#download-button');
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Dropdown behavior', 0, function suite(test) {
    casper.start(document_list_url, function() {
        casper.click('td.columnselect input[type=checkbox]');
        test.assertDoesntExist('.dropdown.open');
    });

    casper.then(function() {
        casper.click('#download-button');
        test.assertExists('.dropdown.open');
    });

    casper.then(function() {
        // A random click does not close the dropdown
        casper.click('body');
        test.assertExists('.dropdown.open');

        casper.click('.dropdown-form button[data-toggle=dropdown]');
        test.assertDoesntExist('.dropdown.open');
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Select all checkbox', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertElementCount('#documents input:checked', 0);
    });

    casper.then(function() {
        casper.click('#select-all');
        test.assertElementCount('#documents input:checked', 2);
    });

    casper.then(function() {
        casper.click('#select-all');
        test.assertElementCount('#documents input:checked', 0);

    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Selecting a row creates an input field in download form', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertDoesntExist('input[name=document_ids]');
    });

    casper.then(function() {
        casper.click('td.columnselect input[type=checkbox]');
        test.assertExists('input[name=document_ids]');
    });

    casper.then(function() {
        casper.click('td.columnselect input[type=checkbox]');
        test.assertDoesntExist('input[name=document_ids]');
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Clicking a row redirects to the document page', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertUrlMatch(/\/organisation_\d+\/category_\d+\/$/);
        casper.click('td.columndocument_key');
    });

    casper.then(function() {
        test.assertUrlMatch(/\/organisation_\d+\/category_\d+\/hazop-report\/$/);
    });

    casper.run(function() {
        test.done();
    });
});
