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
