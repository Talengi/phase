var casper = casper || {};
var phantom = phantom || {};
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

casper.test.begin('Bookmarking a search', 0, function suite(test) {
    casper.start(document_list_url, function() {
        casper.viewport(1024, 768);
        test.assertNotVisible('#bookmark-form');
        casper.click('button#toggle-filters-button');
    });

    casper.then(function() {
        casper.click('button#bookmark-button');
        casper.wait(500);
    });

    casper.then(function() {
        test.assertVisible('#bookmark-modal');
    });

    casper.run(function() {
        test.done();
    });
});
