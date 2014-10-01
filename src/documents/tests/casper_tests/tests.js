var casper = casper || {};
var utils = require('utils');
var document_list_url = casper.cli.options['url'];


casper.options.clientScripts.push("../../../static/js/vendor/sinon.js");


casper.test.begin('Document list tests', 0, function suite(test) {
    casper.start(document_list_url, function() {
        test.assertTitle('Phase');
        casper.wait(500);
        test.assertElementCount('table#documents tbody tr', 1);
        test.assertSelectorHasText('#display-results', '1',
            'Result count is updated');
    });

    casper.run(function() {
        test.done();
    });
});
