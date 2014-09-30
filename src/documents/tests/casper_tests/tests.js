var helper = require('./djangocasper.js');
var server_url = casper.cli.options['url-base'];
var document_list_url = casper.cli.options['url'];

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
        test.assertSelectorHasText('#display-results', '0',
            'Initial result count shows 0');
    });

    casper.run(function() {
        test.done();
    });
});
