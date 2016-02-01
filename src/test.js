casper.start('http://www.google.fr/', function() {
    this.capture('/tmp/capture.png', {
        top: 100,
        left: 100,
        width: 500,
        height: 400
    });
});

casper.run();
