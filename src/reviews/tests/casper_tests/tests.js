var casper = casper || {};
var phantom = phantom || {};
var url = casper.cli.options['url'] + '#fieldset-distribution-list';
var leader_id = casper.cli.options['leader_id'];
var approver_id = casper.cli.options['approver_id'];

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

casper.on('remote.message', function(message) {
    this.echo(message);
});

casper.test.begin('Distribution list fields are empty', 0, function suite(test) {
    casper.start(url, function() {
        casper.viewport(1024, 600);
        // casper.scrollTo(0, 5);
    });

    casper.then(function() {
        casper.wait(500);
    });

    casper.then(function() {
        test.assertNotVisible('#pick-distrib-list-field select');
        test.assertField('leader', '')
        test.assertField('approver', '');
        test.assertField('reviewers', '');

    });

    casper.then(function() {
        test.assertNotVisible('#pick-distrib-list-field .selectize-dropdown')
        casper.click('#pick-distrib-list-field .controls');
        casper.sendKeys('#pick-distrib-list-field input', 'Team', {keepFocus: true});
        casper.wait(500);
    });

    casper.then(function() {
        test.assertVisible('#pick-distrib-list-field .selectize-dropdown')
        test.assertElementCount(
            '#pick-distrib-list-field .selectize-dropdown-content .option', 3);
        test.assertSelectorHasText(
            '#pick-distrib-list-field .selectize-dropdown', 'Team Cassoulet');
    });

    casper.then(function() {
        casper.sendKeys('#pick-distrib-list-field input', ' Cassoulet', {keepFocus: true});
        casper.wait(500);
        test.assertVisible('#pick-distrib-list-field .selectize-dropdown')
        test.assertElementCount(
            '#pick-distrib-list-field .selectize-dropdown-content .option', 2);
        test.assertSelectorHasText(
            '#pick-distrib-list-field .selectize-dropdown', 'Team Cassoulet');
    });

    casper.then(function() {
        casper.sendKeys(
            '#pick-distrib-list-field input',
            casper.page.event.key.Enter);
        casper.wait(500);
        test.assertField('leader', '' + leader_id);
        test.assertField('approver', '' + approver_id);
        casper.capture('/tmp/capture.png');
    });

    casper.run(function() {
        test.done();
    });
});
