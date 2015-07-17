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


casper.test.begin('The remark button displays the message count', 0, function suite(test) {
    casper.start(review_url, function() {
        casper.viewport(1024, 768);
        casper.wait(500);
    });

    casper.then(function() {
        test.assertSelectorHasText('.remarks-button', '10');
    });

    casper.run(function() {
        test.done();
    });
});


casper.test.begin('Discussion is loaded upon page load', 0, function suite(test) {
    casper.start(review_url, function() {
        casper.viewport(1024, 768);
        test.assertNotVisible('#discussion-body');
    });

    casper.then(function() {
        casper.click('button.remarks-button');
        casper.wait(500);
    });

    casper.then(function() {
        test.assertVisible('#discussion-body');
        test.assertElementCount('div.discussion-item', 10);
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Submitting a comment adds it to the list', 0, function suite(test) {
    casper.start(review_url, function() {
        casper.viewport(1024, 768);
        casper.click('button.remarks-button');
        casper.wait(500);
    });

    casper.then(function() {
        casper.fill('#discussion-form form', {
            'body': 'This is a new message.'
        }, true);
        casper.wait(500);
    });

    casper.then(function() {
        test.assertElementCount('div.discussion-item', 11);
        test.assertTextExists('This is a new message');
    });

    casper.run(function() {
        test.done();
    });
});

casper.test.begin('Clicking on edit button shows the edit form', 0, function suite(test) {
    casper.start(review_url, function() {
        casper.viewport(1024, 768);
        casper.click('button.remarks-button');
        casper.wait(500);
    });

    casper.then(function() {
        test.assertNotVisible('form.edit-form');
        test.assertTextDoesntExist('Edited text');
        casper.click('a.edit-link');
    });

    casper.then(function() {
        test.assertVisible('form.edit-form');
        casper.fill('form.edit-form', {
            'body': 'Edited text'
        }, true);
        casper.wait(500);
    });

    casper.then(function() {
        test.assertNotVisible('form.edit-form');
        test.assertTextExists('Edited text');
    });

    casper.run(function() {
        test.done();
    });
});
