var casper = casper || {};
var phantom = phantom || {};
var review_url = casper.cli.options['url'];

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


casper.test.begin('Discussion is loaded upon page load', 0, function suite(test) {
    casper.start(review_url, function() {
        casper.viewport(1024, 768);
        test.assertNotVisible('#discussion-body');
    });

    casper.then(function() {
        casper.click('button#remarks-button');
        casper.wait(500);
    });

    casper.then(function() {
        test.assertVisible('#discussion-body');
        test.assertElementCount('div.note', 10);
    });

    casper.run(function() {
        test.done();
    });
});
